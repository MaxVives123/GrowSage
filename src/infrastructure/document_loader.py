"""Document loading, chunking, and ID generation."""
from __future__ import annotations
import hashlib
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def load_pdf(path: str) -> list:
    return PyPDFLoader(path).load()


def load_txt(path: str) -> list:
    return TextLoader(path, encoding="utf-8").load()


def load_url(url: str) -> list:
    return WebBaseLoader(url).load()


def load_folder(folder: str = "data") -> list:
    docs = []
    for f in Path(folder).rglob("*.pdf"):
        print(f"  PDF: {f}")
        docs.extend(load_pdf(str(f)))
    for f in Path(folder).rglob("*.txt"):
        print(f"  TXT: {f}")
        docs.extend(load_txt(str(f)))
    return docs


def split_documents(docs: list) -> list:
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    ).split_documents(docs)


def make_doc_id(doc) -> str:
    source = doc.metadata.get("source", "")
    page = doc.metadata.get("page", 0)
    digest = hashlib.md5(doc.page_content.encode()).hexdigest()[:8]
    return f"{source}::{page}::{digest}"
