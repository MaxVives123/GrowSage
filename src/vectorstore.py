from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

PERSIST_DIR = "vectorstore"
COLLECTION = "botanica_huerto"


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model="text-embedding-3-small")


def get_store() -> Chroma:
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=get_embeddings(),
        persist_directory=PERSIST_DIR,
    )


def _doc_id(doc) -> str:
    import hashlib
    source = doc.metadata.get("source", "")
    page = doc.metadata.get("page", 0)
    content_hash = hashlib.md5(doc.page_content.encode()).hexdigest()[:8]
    return f"{source}::{page}::{content_hash}"


def add_documents(docs: list) -> Chroma:
    store = get_store()
    existing = set(store.get()["ids"])
    ids = [_doc_id(d) for d in docs]
    new_docs = [(doc, id_) for doc, id_ in zip(docs, ids) if id_ not in existing]
    if not new_docs:
        print("  Sin documentos nuevos — todo ya estaba indexado.")
        return store
    new_doc_list, new_ids = zip(*new_docs)
    store.add_documents(list(new_doc_list), ids=list(new_ids))
    print(f"  {len(new_doc_list)} fragmentos nuevos indexados ({len(docs) - len(new_doc_list)} ya existían).")
    return store


def get_retriever(k: int = 5):
    store = get_store()
    return store.as_retriever(search_type="mmr", search_kwargs={"k": k, "fetch_k": 20})
