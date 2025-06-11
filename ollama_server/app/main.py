from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
import os
import datetime
import json
import requests

from app.train import process_file, list_datasets_with_counts, purge_dataset
from app.query import search_and_respond, search_context_for_prompt
from app.config_loader import get_num_predict_for

# Initialize FastAPI app
app = FastAPI()

# Set up templates directory
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

# Ensuring upload directory exists
UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Pydantic model for streaming query input
class StreamQuery(BaseModel):
    question: str
    dataset: str | None = None

# Home page: Render chat interface with available datasets
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    datasets = list_datasets_with_counts()
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "datasets": datasets
    })

# Endpoint to upload and train on a new file
# TO-DO: Return the error if uploaded file is unsupported.
# TO-DO: Add auto-refresh mechanism once training is completed on a new dataset.
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

# Endpoint for submitting a question and getting a response
# TO-DO: Clean the input to avoid non-ascii characters
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

# Endpoint to purge (delete) a trained dataset
# TO-DO: Add a pop-up message feature once the dataset is purged.
@app.post("/purge")
async def purge_dataset_handler(request: Request, dataset: str = Form(...)):
    datasets = list_datasets_with_counts()
    try:
        message = purge_dataset(dataset)
        datasets = list_datasets_with_counts()  # Refresh after purge
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

# Streaming API endpoint that uses Ollama for long responses
@app.post("/ask_stream")
async def ask_stream(request: StreamQuery):
    question = request.question
    dataset = request.dataset

    # Get relevant context for question
    context = search_context_for_prompt(question, dataset)
    full_prompt = f"""Use the below context to answer the question.
Context:
{context}

Question:
{question}
"""

    num_predict = get_num_predict_for(dataset or "default")

    def generate():
        # Stream response from Ollama backend
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
                    yield json.loads(text).get("response", "")
                except Exception:
                    pass

        # Log the full raw response
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        filename = f"{log_dir}/response_{dataset or 'general'}_{timestamp}.log"
        with open(filename, "w") as f:
            f.write(log_content)

    return StreamingResponse(generate(), media_type="text/plain")
