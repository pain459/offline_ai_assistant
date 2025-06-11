"""
Purpose:
This module handles dataset ingestion, storage, and management for semantic search.
It uses SentenceTransformers to encode documents into embeddings and stores them in
a FAISS vector index for fast similarity search. Metadata is persisted using pickle.

Workflow:
1. Upload a file via API.
2. `process_file()` validates, reads, chunks, and encodes the file, then stores embeddings.
3. A mapping between each chunk and its dataset name is stored using pickle.
4. `purge_dataset()` allows removal of a dataset by name.
5. `list_datasets_with_counts()` returns available datasets and chunk counts.
"""

import os
import pickle
import faiss
import logging
from sentence_transformers import SentenceTransformer
from app.utils import validate_file_type, read_file_content, chunk_text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

# Global settings
model = SentenceTransformer("all-MiniLM-L6-v2")  # Balanced speed and performance
embedding_dim = 384                              # Embedding dimensionality of the model
index_path = "vector_store.index"                # FAISS index file
mapping_path = "index_mapping.pkl"               # Pickled metadata file (chunk, dataset)


def dataset_exists(dataset_name: str) -> bool:
    """
    Checks if the dataset already exists in the mapping file.
    """
    if not os.path.exists(mapping_path):
        return False

    with open(mapping_path, "rb") as f:
        mapping = pickle.load(f)

    exists = any(tag == dataset_name for _, tag in mapping)
    logger.debug(f"Dataset '{dataset_name}' exists: {exists}")
    return exists


def process_file(file_path: str) -> str:
    """
    Processes an uploaded file:
    - Validates the file type
    - Reads and chunks the content
    - Encodes chunks into embeddings
    - Updates FAISS index and mapping with new entries
    """
    try:
        ext = validate_file_type(file_path)
        dataset_name = os.path.splitext(os.path.basename(file_path))[0]
        logger.info(f"Processing dataset: {dataset_name} from file: {file_path}")

        if dataset_exists(dataset_name):
            raise Exception(f"Dataset '{dataset_name}' already exists. Please purge it first if you want to re-upload.")

        text = read_file_content(file_path, ext)
        chunks = chunk_text(text)
        vectors = model.encode(chunks)

        # Load existing index and mapping
        if os.path.exists(index_path) and os.path.exists(mapping_path):
            index = faiss.read_index(index_path)
            with open(mapping_path, "rb") as f:
                mapping = pickle.load(f)
        else:
            index = faiss.IndexFlatL2(embedding_dim)
            mapping = []

        # Add and persist
        index.add(vectors)
        mapping.extend([(chunk, dataset_name) for chunk in chunks])

        faiss.write_index(index, index_path)
        with open(mapping_path, "wb") as f:
            pickle.dump(mapping, f)

        logger.info(f"Successfully added {len(chunks)} chunks to dataset '{dataset_name}'")
        return f"Added {len(chunks)} chunks to dataset '{dataset_name}'."

    except Exception as e:
        logger.exception(f"Failed to process file {file_path}: {e}")
        raise


def purge_dataset(dataset_name: str) -> str:
    """
    Removes all entries belonging to a specific dataset from the index and mapping.
    Rebuilds the FAISS index with the remaining entries.
    """
    try:
        if not os.path.exists(index_path) or not os.path.exists(mapping_path):
            raise Exception("No training data found.")

        with open(mapping_path, "rb") as f:
            mapping = pickle.load(f)

        remaining = [(chunk, tag) for chunk, tag in mapping if tag != dataset_name]
        removed_count = len(mapping) - len(remaining)

        if removed_count == 0:
            raise Exception(f"No dataset named '{dataset_name}' found.")

        new_index = faiss.IndexFlatL2(embedding_dim)
        if remaining:
            texts = [chunk for chunk, _ in remaining]
            vectors = model.encode(texts)
            new_index.add(vectors)

        faiss.write_index(new_index, index_path)
        with open(mapping_path, "wb") as f:
            pickle.dump(remaining, f)

        logger.info(f"✅ Purged dataset '{dataset_name}', removed {removed_count} entries.")
        return f"✅ Removed {removed_count} entries from dataset '{dataset_name}'."

    except Exception as e:
        logger.exception(f"Failed to purge dataset '{dataset_name}': {e}")
        raise


def list_datasets_with_counts():
    """
    Returns a sorted list of datasets with the count of their associated text chunks.
    Example: [("dataset1", 24), ("dataset2", 12)]
    """
    try:
        if not os.path.exists(mapping_path):
            logger.info("No datasets found. Mapping file does not exist.")
            return []

        with open(mapping_path, "rb") as f:
            mapping = pickle.load(f)

        dataset_counts = {}
        for _, tag in mapping:
            dataset_counts[tag] = dataset_counts.get(tag, 0) + 1

        logger.info(f"Loaded {len(dataset_counts)} dataset(s).")
        return sorted(dataset_counts.items())

    except Exception as e:
        logger.exception(f"Failed to list datasets: {e}")
        return []
