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


def load_data_folder(folder: str = "data") -> list:
    docs = []
    data_path = Path(folder)
    for f in data_path.rglob("*.pdf"):
        print(f"  PDF: {f}")
        docs.extend(load_pdf(str(f)))
    for f in data_path.rglob("*.txt"):
        print(f"  TXT: {f}")
        docs.extend(load_txt(str(f)))
    return docs


def split_documents(docs: list) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(docs)
