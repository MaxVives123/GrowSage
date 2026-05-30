"""Chat use case — orchestrates VectorStore + LLM to answer a question."""
from __future__ import annotations
from typing import Iterator
from src.domain.interfaces import IVectorStore, ILLM
from src.domain.models import ChatAnswer, SearchResult


class ChatService:
    def __init__(self, vector_store: IVectorStore, llm: ILLM) -> None:
        self._store = vector_store
        self._llm = llm

    def get_sources(self, question: str, k: int = 5) -> list[SearchResult]:
        return self._store.search(question, k=k)

    def answer(self, question: str, history: list[dict] = None) -> ChatAnswer:
        """Non-streaming answer — used by backward-compat endpoint and tests."""
        results = self.get_sources(question)
        context = self._build_context(results)
        answer_text = self._llm.generate(question, context, history or [])
        return ChatAnswer(answer=answer_text, sources=results[:3])

    def stream_answer(
        self, question: str, history: list[dict] = None
    ) -> tuple[list[SearchResult], Iterator[str]]:
        """Returns (sources, token_iterator) for SSE streaming."""
        results = self.get_sources(question)
        context = self._build_context(results)
        return results[:3], self._llm.stream(question, context, history or [])

    @staticmethod
    def _build_context(results: list[SearchResult]) -> str:
        return "\n\n---\n\n".join(
            f"[Source: {r.source}, p.{r.page}]\n{r.content}"
            for r in results
        )
