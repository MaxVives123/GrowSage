"""ChromaDB adapter — implements IVectorStore."""
from __future__ import annotations
import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from src.domain.interfaces import IVectorStore
from src.domain.models import SearchResult


class ChromaVectorStore(IVectorStore):
    def __init__(
        self,
        persist_dir: str | None = None,
        collection: str = "botanica_huerto",
    ) -> None:
        if persist_dir is None:
            persist_dir = os.getenv("CHROMA_PERSIST_DIR", "vectorstore")
        self._store = Chroma(
            collection_name=collection,
            embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
            persist_directory=persist_dir,
        )

    def search(self, query: str, k: int = 5) -> list[SearchResult]:
        retriever = self._store.as_retriever(
            search_type="mmr", search_kwargs={"k": k, "fetch_k": 20}
        )
        docs = retriever.invoke(query)
        results = []
        for doc in docs:
            raw = doc.metadata.get("source", "Unknown")
            name = (
                raw.replace("data\\", "")
                   .replace("data/", "")
                   .replace(".pdf", "")
                   .replace("_", " ")
                   .title()
            )
            page = doc.metadata.get("page", "")
            results.append(SearchResult(
                content=doc.page_content,
                source=name,
                page=str(page + 1) if isinstance(page, int) else str(page),
            ))
        return results

    def add_documents(self, docs: list, ids: list[str]) -> None:
        existing = set(self._store.get()["ids"])
        pairs = [(d, i) for d, i in zip(docs, ids) if i not in existing]
        if not pairs:
            return
        new_docs, new_ids = zip(*pairs)
        self._store.add_documents(list(new_docs), ids=list(new_ids))
