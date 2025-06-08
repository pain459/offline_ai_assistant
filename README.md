# 🧠 Offline AI Assistant

The **Offline AI Assistant** is a self-hosted, privacy-first tool that allows you to upload files like **PDF, CSV, TXT, Excel**, and **ask questions** about them using a local LLM such as **LLaMA3 via Ollama** — all without internet access.

There’s no data going to the cloud, no subscriptions, and no cost. Just **boot it up when you need**, upload a file, and start querying it from your browser.

---

### ⚙️ Core Logic

1. **Upload** a file using the web form (`chat.html`)
2. File is **split into chunks**, embedded, and stored under `/data/<dataset_name>/` using FAISS.
3. When a question is asked:
   - Relevant context is fetched via **semantic vector search**
   - A prompt is built combining context + question
   - It is sent to **Ollama**, which responds with the answer

All processing happens **entirely locally** using FastAPI and Ollama.

---

### 🔌 API Endpoints

| Method | Endpoint      | Description                          |
|--------|---------------|--------------------------------------|
| GET    | `/`           | Load the HTML-based UI               |
| POST   | `/upload`     | Upload and train on a new file       |
| POST   | `/query`      | Ask a question on a trained dataset  |
| POST   | `/purge`      | Delete a dataset                     |
| GET    | `/datasets`   | Get list of available datasets       |

---

### 🚀 Usage

1. **Clone the project**

```bash
git clone https://github.com/pain459/offline_ai_assistant.git
cd offline_ai_assistant
```

2. **Boot with Docker**

```bash
docker-compose up --build
```

3. **Visit the UI**

Go to: [http://localhost:8000](http://localhost:8000)

- Upload a file (e.g., `.pdf`)
- Select the dataset
- Ask your question
- View AI-generated answers based only on your file

4. **Remove datasets** using the "Purge Dataset" option

---

### 📄 Supported File Types

- `.pdf`
- `.txt`
- `.csv`
- `.xlsx`
- `.json`

Extendable via `train.py`.

---

### 🖥 Requirements

- Docker + Docker Compose
- At least 8GB RAM (16GB+ recommended for larger files/models)
- Optional GPU (CUDA or Apple Silicon supported by Ollama)

---

### 📈 Scalability Notes

- You can extend the assistant with:
  - ✅ Auth for private access
  - ✅ Streaming Markdown UI
  - ✅ Replace FAISS with Weaviate/Qdrant for production search
  - ✅ Add persistent SQLite logs
  - ✅ Deploy on local network with port exposure

This setup is designed to remain **lightweight and fast** while remaining private and offline.

---

### 🚧 Current State of the Project

This project is currently in an **alpha** state and under active development. Here are a few notes to set expectations:

1. **Codebase is still evolving**  
   There are areas that need cleanup and refactoring. Please avoid judging the structure or code quality just yet.

2. **Documentation and comments are being added**  
   We're working on improving inline comments and adding clearer explanations throughout the code.

3. **UI is functional but minimal**  
   The current user interface is basic and serves the core functionality. It will be improved in upcoming updates.

4. **Hardcoded values exist**  
   Some parts of the code use hardcoded values. These will be made configurable as development progresses.

---

### 🤝 Contribution

Welcome to contributions!

1. Fork this repository
2. Create a new feature branch
3. Submit a pull request

Suggestions for improvement include:
- Advanced file parsing (tables, scanned PDFs)
- Multiple file training
- File comparison Q&A
- Multilingual support

---

MIT License
