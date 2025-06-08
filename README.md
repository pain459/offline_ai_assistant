````markdown
# 🧠 Offline AI Assistant

A **fully offline AI assistant** that lets you upload your own files—PDFs, CSVs, TXT, etc.—and ask intelligent questions about them using a locally running LLM like **LLaMA3** (via [Ollama](https://ollama.com)).

No cloud. No subscriptions. No data leaving your machine.

---

## ✅ Why Use This?

- 🔐 **Your data stays local** – zero risk of leaks
- 🆓 **Completely free** – no API costs or token limits
- ⚡ **Boot when needed** – start/stop with Docker Compose
- 📄 **Ask anything about your files** – document Q&A made simple
- 🐳 **Runs in Docker** – portable, secure, and isolated

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/offline_ai_assistant.git
cd offline_ai_assistant
````

### 2. Start with Docker

```bash
docker-compose up --build
```

> This launches:
>
> * FastAPI backend
> * Ollama model container (e.g., LLaMA3)

---

## 🌐 Access the Web Interface

Visit:

```
http://localhost:8000
```

From there, you can:

* 📁 Upload a file (PDF, CSV, TXT, etc.)
* ❓ Ask questions about its contents
* 🧹 Purge datasets anytime

---

## 🧩 System Design Diagram

```
              ┌─────────────────────────────┐
              │         Web UI              │
              │   (chat.html via FastAPI)   │
              └────────────┬────────────────┘
                           │
          ┌────────────────▼────────────────┐
          │            FastAPI              │
          │            main.py              │
          └────────────────┬────────────────┘
                           │
         ┌─────────────────┼────────────────────┐
         │                 │                    │
         ▼                 ▼                    ▼
 ┌────────────┐   ┌────────────────────┐  ┌──────────────────┐
 │  train.py  │   │     query.py       │  │ config_loader.py │
 │ (vectorize)│   │ (semantic search + │  │  (settings like  │
 │            │   │   LLM interaction) │  │   token limits)  │
 └────┬───────┘   └──────────┬─────────┘  └──────────────────┘
      │                     │
      ▼                     ▼
┌──────────────┐     ┌──────────────┐
│ /data folder │     │   Ollama     │
│(dataset store│     │(LLM service) │
│  on disk)    │     └──────────────┘
└──────────────┘
```

---

## 🔄 Data Flow Diagram

```
                 User
                  │
                  ▼
        ┌──────────────────┐
        │ Upload a File    │
        │ (via chat.html)  │
        └────────┬─────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ FastAPI `/upload`  │
        └────────┬───────────┘
                 ▼
        ┌────────────────────┐
        │    train.py        │
        │ - Parse file       │
        │ - Embed with model │
        │ - Store in /data   │
        └────────┬───────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ Ask a Question     │
        │ (via chat.html)    │
        └────────┬───────────┘
                 ▼
        ┌────────────────────┐
        │ FastAPI `/query`   │
        └────────┬───────────┘
                 ▼
        ┌────────────────────┐
        │   query.py         │
        │ - Search vectors   │
        │ - Select context   │
        └────────┬───────────┘
                 ▼
        ┌────────────────────┐
        │     Ollama         │
        │  (e.g., LLaMA3)    │
        └────────┬───────────┘
                 ▼
        ┌────────────────────┐
        │ Return Answer      │
        │ (stream to UI)     │
        └────────────────────┘
```

---

## 🧰 Low-Level Design

### 📁 Folder Structure

```
offline_ai_assistant/
├── main.py                # FastAPI app with routes
├── train.py               # Embeds uploaded files
├── query.py               # Performs vector search + LLM prompt
├── config_loader.py       # Token config loader
├── requirements.txt       # Python dependencies
├── Dockerfile             # FastAPI build config
├── docker-compose.yml     # Orchestrates API + Ollama
├── templates/
│   └── chat.html          # Minimal web UI
├── data/
│   └── <dataset_name>/    # Vector storage
```

---

### 🔌 API Endpoints

| Method | Endpoint    | Description             |
| ------ | ----------- | ----------------------- |
| GET    | `/`         | UI home page            |
| POST   | `/upload`   | Train on uploaded file  |
| POST   | `/query`    | Ask a question          |
| POST   | `/purge`    | Remove dataset          |
| GET    | `/datasets` | List available datasets |

---

### 🧠 Core Logic

**Embedding Flow** (`train.py`)

```python
def process_file(file, dataset_name):
    chunks = split_file_into_chunks(file)
    embeddings = model.encode(chunks)
    save_as_faiss(embeddings, dataset_name)
```

**Query Flow** (`query.py`)

```python
def search_and_respond(dataset, question):
    context = top_k_similar_chunks(question, dataset)
    prompt = f"{context}\n\nQ: {question}"
    return query_ollama(prompt)
```

**Ollama Streaming**

```python
def query_ollama(prompt):
    yield from requests.post("http://ollama:11434/api/generate", json={
        "model": "llama3",
        "prompt": prompt,
        "stream": True
    }, stream=True).iter_lines()
```

---

## 📄 Supported File Types

* `.pdf`
* `.txt`
* `.csv`
* `.xlsx`
* `.json`

You can extend file handling in `train.py`.

---

## 🧹 Remove Dataset

Use the “Purge Dataset” button or call the `/purge` endpoint to delete a dataset folder from `/data/`.

---

## 🛠 Requirements

* Docker + Docker Compose
* 8GB+ RAM (16GB recommended)
* GPU support optional (Ollama supports CUDA & Apple Metal)

---

## 📈 Scalability Notes

| Area         | Future Ideas                                       |
| ------------ | -------------------------------------------------- |
| UI           | Add streaming, markdown, and chat history          |
| Persistence  | Use SQLite or LiteDB to track session logs         |
| Vector Store | Swap FAISS with Qdrant/Weaviate for production use |
| Auth         | Add basic token auth for multi-user access         |
| Model        | Swap Ollama for LM Studio, llama.cpp, or local API |

---

## 🙌 Contributing

1. Fork the repo
2. Create your branch
3. Submit a PR

Open to improvements in:

* File parsing
* Model routing
* UI enhancements

---

## 📜 License

MIT License. See `LICENSE`.

---
