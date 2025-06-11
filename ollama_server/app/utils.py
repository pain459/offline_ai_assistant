"""
Purpose:
    This utility module provides functions to:
    1. Validate supported file types (PDF, CSV, TXT).
    2. Read and extract textual content from these file types.
    3. Chunk large text into smaller segments for further processing, such as embedding or model inference.

Supported Formats:
    - PDF: Extracts text from all pages using PyMuPDF.
    - CSV: Converts tabular data to a string representation.
    - TXT: Reads the entire file as plain text.
    - JSON: Loads JSON and returns a pretty-printed string.
"""

import os
import pandas as pd
import json
import fitz  # PyMuPDF

def validate_file_type(file_path: str):
    """
    Validates whether the given file has a supported extension.

    Args:
        file_path (str): Full path to the file.

    Returns:
        str: File extension if valid.

    Raises:
        Exception: If the file extension is not among supported types.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in [".pdf", ".csv", ".txt", ".json"]:
        # TO-DO: Add logging if the file type is invalid.
        raise Exception(f"Unsupported file type: {ext}")
    return ext

def read_file_content(file_path: str, ext: str) -> str:
    """
    Reads and extracts content from a file based on its extension.

    Args:
        file_path (str): Path to the file.
        ext (str): File extension (must be validated beforehand).

    Returns:
        str: Extracted text content.

    Raises:
        Exception: If extension is unsupported.
    """
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif ext == ".csv":
        df = pd.read_csv(file_path)
        return df.to_string()
    elif ext == ".pdf":
        doc = fitz.open(file_path)
        return "\n".join(page.get_text() for page in doc)
    elif ext == ".json":
        # Read and pretty-print JSON content
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, indent=2)
    else:
        raise Exception("Unsupported file extension")

def chunk_text(text: str, chunk_size=500):
    """
    Splits a large text into smaller chunks.

    Args:
        text (str): The complete text to be split.
        chunk_size (int, optional): Maximum number of characters per chunk. Defaults to 500.

    Returns:
        list[str]: A list of text chunks.
    """
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
