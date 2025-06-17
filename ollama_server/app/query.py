"""
Purpose:
This script performs semantic search and response generation for an offline AI assistant.
It uses FAISS for vector similarity search and a locally hosted LLM (via Ollama) to answer 
user queries based on indexed document chunks. The system ensures fast, local, and private
question answering.

This script uses `lru_cache` to memoize the results of expensive operations like:
- Loading the SentenceTransformer model
- Reading the FAISS index
- Unpickling the index-to-chunk mapping
This improves response speed and conserves system resources across repeated queries.

Workflow:
1. Load sentence transformer model, FAISS index, and index-to-text mapping (cached).
2. Convert user query into vector and perform FAISS search.
3. Retrieve top context chunks relevant to the query and dataset.
4. Construct a prompt using the context and query.
5. Send the prompt to the Ollama LLM and return the generated response.
6. Optionally, fetch only the context chunks for a query without generating a response.
"""

import os
import faiss
import pickle
from functools import lru_cache
from sentence_transformers import SentenceTransformer
import requests
from app.config_loader import get_num_predict_for

# Constants for file paths and model endpoint
INDEX_FILE = "vector_store.index"          # FAISS index file containing vectorized document chunks
MAPPING_FILE = "index_mapping.pkl"         # Pickle file mapping vector positions to original chunks and dataset names
OLLAMA_URL = "http://ollama:11434/api/generate"  # Local Ollama LLM API endpoint


# Caches the loaded transformer model in memory.
@lru_cache()
def get_model():
    return SentenceTransformer("/root/.cache/torch/sentence_transformers/sentence-transformers_all-MiniLM-L6-v2")  # We will use local model instead which is installed via pip.

# Caches the FAISS index after first load from disk.
@lru_cache()
def get_index():
    if not os.path.exists(INDEX_FILE):
        raise FileNotFoundError("Vector index not found.")
    return faiss.read_index(INDEX_FILE)

# Caches the index-to-chunk mapping from a pickle file.
@lru_cache()
def get_mapping():
    if not os.path.exists(MAPPING_FILE):
        raise FileNotFoundError("Mapping file not found.")
    with open(MAPPING_FILE, "rb") as f:
        return pickle.load(f)

# Search the vector store for relevant context and generate a response using Ollama
def search_and_respond(question: str, dataset_name: str = None) -> str:
    model = get_model()
    index = get_index()
    mapping = get_mapping()

    # Convert question to embedding vector
    q_vec = model.encode([question])
    D, I = index.search(q_vec, 10)  # Search for top 10 similar vectors

    context_chunks = []
    for i in I[0]:
        if i >= len(mapping):
            continue
        chunk, tag = mapping[i]
        if dataset_name is None or tag == dataset_name:
            context_chunks.append(chunk)
        if len(context_chunks) >= 3:  # Limit context to top 3 chunks
            break

    if not context_chunks:
        return f"No data found for dataset: '{dataset_name}'"

    # Construct prompt for the model
    prompt = f"""Use the below context to answer the question.
Context:
{chr(10).join(context_chunks)}

Question:
{question}
"""

    # Call Ollama model with constructed prompt
    response = requests.post(OLLAMA_URL, json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": get_num_predict_for(dataset_name)  # Limit tokens generated
        }
    })

    # Return the model's response text or a fallback
    return response.json().get("response", "[No response]")

# Just return the relevant context chunks for a query (no LLM response)
def search_context_for_prompt(query: str, dataset: str = None, top_k: int = 5) -> str:
    model = get_model()
    index = get_index()
    mapping = get_mapping()

    # Embed the query and search for top_k similar entries
    query_vector = model.encode([query])
    D, I = index.search(query_vector, top_k)

    context_chunks = []
    for idx in I[0]:
        if idx >= len(mapping):
            continue
        chunk, chunk_dataset = mapping[idx]
        if dataset is None or chunk_dataset == dataset:
            context_chunks.append(chunk)

    # Return joined context for inspection or downstream processing
    return "\n".join(context_chunks)
