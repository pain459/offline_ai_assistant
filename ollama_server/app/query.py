import os
import faiss
import pickle
from functools import lru_cache
from sentence_transformers import SentenceTransformer
import requests
from app.config_loader import get_num_predict_for

INDEX_FILE = "vector_store.index"
MAPPING_FILE = "index_mapping.pkl"
OLLAMA_URL = "http://ollama:11434/api/generate"


@lru_cache()
def get_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


@lru_cache()
def get_index():
    if not os.path.exists(INDEX_FILE):
        raise FileNotFoundError("Vector index not found.")
    return faiss.read_index(INDEX_FILE)


@lru_cache()
def get_mapping():
    if not os.path.exists(MAPPING_FILE):
        raise FileNotFoundError("Mapping file not found.")
    with open(MAPPING_FILE, "rb") as f:
        return pickle.load(f)


def search_and_respond(question: str, dataset_name: str = None) -> str:
    model = get_model()
    index = get_index()
    mapping = get_mapping()

    q_vec = model.encode([question])
    D, I = index.search(q_vec, 10)

    context_chunks = []
    for i in I[0]:
        if i >= len(mapping):
            continue
        chunk, tag = mapping[i]
        if dataset_name is None or tag == dataset_name:
            context_chunks.append(chunk)
        if len(context_chunks) >= 3:
            break

    if not context_chunks:
        return f"No data found for dataset: '{dataset_name}'"

    prompt = f"""Use the below context to answer the question.
Context:
{chr(10).join(context_chunks)}

Question:
{question}
"""

    response = requests.post(OLLAMA_URL, json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": get_num_predict_for(dataset_name)
        }
    })

    return response.json().get("response", "[No response]")


def search_context_for_prompt(query: str, dataset: str = None, top_k: int = 5) -> str:
    model = get_model()
    index = get_index()
    mapping = get_mapping()

    query_vector = model.encode([query])
    D, I = index.search(query_vector, top_k)

    context_chunks = []
    for idx in I[0]:
        if idx >= len(mapping):
            continue
        chunk, chunk_dataset = mapping[idx]
        if dataset is None or chunk_dataset == dataset:
            context_chunks.append(chunk)

    return "\n".join(context_chunks)
