import os
import pandas as pd
import fitz  # PyMuPDF

def validate_file_type(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in [".pdf", ".csv", ".txt"]:
        # TO-DO: Add logging if the file type is invalid.
        raise Exception(f"Unsupported file type: {ext}")
    return ext

def read_file_content(file_path: str, ext: str) -> str:
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif ext == ".csv":
        df = pd.read_csv(file_path)
        return df.to_string()
    elif ext == ".pdf":
        doc = fitz.open(file_path)
        return "\n".join(page.get_text() for page in doc)
    else:
        raise Exception("Unsupported file extension")

def chunk_text(text: str, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
