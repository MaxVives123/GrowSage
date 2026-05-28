"""Chat use case — orchestrates VectorStore + LLM to answer a question."""
from __future__ import annotations
from src.domain.interfaces import IVectorStore, ILLM
from src.domain.models import ChatAnswer


class ChatService:
    def __init__(self, vector_store: IVectorStore, llm: ILLM) -> None:
        self._store = vector_store
        self._llm = llm

    def answer(self, question: str) -> ChatAnswer:
        results = self._store.search(question, k=5)
        context = "\n\n---\n\n".join(
            f"[Source: {r.source}, p.{r.page}]\n{r.content}"
            for r in results
        )
        answer_text = self._llm.generate(question, context)
        return ChatAnswer(answer=answer_text, sources=results[:3])
