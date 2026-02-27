"""
Document Loader Utility
Supports PDF and DOCX file formats for CV/Resume parsing
"""
from pathlib import Path
from typing import List
from langchain_core.documents import Document

SUPPORTED_FORMATS = [".pdf", ".docx", ".txt"]


def load_document(file_path: str) -> List[Document]:
    """
    Load a document from the given file path.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        List of Document objects containing the file content
        
    Raises:
        ValueError: If the file format is not supported
    """
    path = Path(file_path)
    file_extension = path.suffix.lower()
    
    if file_extension not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported file format: {file_extension}. Supported formats: {SUPPORTED_FORMATS}")
    
    if file_extension == ".pdf":
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(str(path))
        return loader.load()
    
    elif file_extension == ".docx":
        from langchain_community.document_loaders import Docx2txtLoader
        loader = Docx2txtLoader(str(path))
        return loader.load()
    
    elif file_extension == ".txt":
        from langchain_community.document_loaders import TextLoader
        loader = TextLoader(str(path), encoding="utf-8")
        return loader.load()
    
    return []


def get_document_content(file_path: str) -> str:
    """
    Load a document and return its content as a single string.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        The full text content of the document
    """
    docs = load_document(file_path)
    return "\n\n".join(doc.page_content for doc in docs)
