import os
from typing import List

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")
DATA_DIR = os.path.abspath(DATA_DIR)

def ensure_data_dir():
    """create the data dir if it doesnt exist"""
    os.makedirs(DATA_DIR, exist_ok = True)

def save_document(filename: str, content: bytes) -> str:
    """
    save a doc to the data dir.
    returns the full path to the saved file.
    """
    ensure_data_dir()
    file_path = os.path.join(DATA_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path

def read_documents(filename: str) -> bytes:
    """
    read a  document from the data dir.
    returns the file content as bytes.    
    """
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Document '{filename}' not found")
    
    with open(file_path, "rb") as f:
        return f.read()

def list_documents() -> List[str]:
    """
    lists all docs in the data directory.
    returns a list of filenames
    """
    ensure_data_dir()
    return [f for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f))]