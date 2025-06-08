from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from .train import process_file
from fastapi import Form
from .query import search_and_respond
from pathlib import Path
from .train import list_datasets_with_counts, purge_dataset
from fastapi.responses import StreamingResponse
from .config_loader import get_num_predict_for
import datetime
from pydantic import BaseModel

app = FastAPI()
# templates = Jinja2Templates(directory="templates")
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# @app.get("/", response_class=HTMLResponse)
# async def index(request: Request):
#     datasets = list_datasets_with_counts()
#     return templates.TemplateResponse("chat.html", {
#         "request": request,
#         "datasets": datasets
#     })


class StreamQuery(BaseModel):
    question: str
    dataset: str | None = None

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    from .train import list_datasets_with_counts
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "datasets": list_datasets_with_counts()
    })


@app.post("/train")
async def train(request: Request, file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        result = process_file(file_path)
        return templates.TemplateResponse("chat.html", {
            "request": request,
            "message": f"Training complete: {result}"
        })
    except Exception as e:
        return templates.TemplateResponse("chat.html", {
            "request": request,
            "error": str(e)
        })
@app.post("/ask")
async def ask_question(request: Request, question: str = Form(...), dataset: str = Form(None)):
    try:
        answer = search_and_respond(question, dataset_name=dataset)
        return templates.TemplateResponse("chat.html", {
            "request": request,
            "answer": answer,
            "question": question,
            "dataset": dataset
        })
    except Exception as e:
        return templates.TemplateResponse("chat.html", {
            "request": request,
            "error": str(e)
        })
@app.post("/purge")
async def purge_dataset_handler(request: Request, dataset: str = Form(...)):
    datasets = list_datasets_with_counts()
    try:
        message = purge_dataset(dataset)
        datasets = list_datasets_with_counts()  # Refresh list after purge
        return templates.TemplateResponse("chat.html", {
            "request": request,
            "message": message,
            "datasets": datasets
        })
    except Exception as e:
        return templates.TemplateResponse("chat.html", {
            "request": request,
            "error": str(e),
            "datasets": datasets
        })

@app.post("/ask_stream")
async def ask_stream(request: StreamQuery):
    from .query import search_context_for_prompt
    question = request.question
    dataset = request.dataset

    context = search_context_for_prompt(question, dataset)
    full_prompt = f"""Use the below context to answer the question.
Context:
{context}

Question:
{question}
"""

    num_predict = get_num_predict_for(dataset or "default")

    def generate():
        import requests
        response = requests.post("http://ollama:11434/api/generate", json={
            "model": "llama3",
            "prompt": full_prompt,
            "stream": True,
            "options": {
                "num_predict": num_predict
            }
        }, stream=True)

        log_content = ""
        for line in response.iter_lines():
            if line:
                text = line.decode("utf-8")
                log_content += text + "\n"
                try:
                    import json
                    yield json.loads(text).get("response", "")
                except Exception:
                    pass

        # Save log
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"logs/response_{dataset or 'general'}_{timestamp}.log"
        os.makedirs("logs", exist_ok=True)
        with open(filename, "w") as f:
            f.write(log_content)

    return StreamingResponse(generate(), media_type="text/plain")
