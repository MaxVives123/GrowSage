"""OpenAI/LangChain adapter — implements ILLM."""
from __future__ import annotations
from typing import Iterator
import openai
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from src.domain.interfaces import ILLM

_SYSTEM_TEMPLATE = """You are an expert in horticulture and edible plant cultivation.
Use ONLY the information from the provided context to answer.
If the answer is not in the context, say so clearly and suggest where to look.
Answer in the same language as the question. Be practical and direct.

Context:
{context}
"""


class OpenAILLM(ILLM):
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.2) -> None:
        self._llm = ChatOpenAI(model=model, temperature=temperature)

    def _build_messages(self, question: str, context: str, history: list[dict]) -> list:
        msgs = [SystemMessage(content=_SYSTEM_TEMPLATE.format(context=context))]
        for h in history:
            if h["role"] == "user":
                msgs.append(HumanMessage(content=h["content"]))
            else:
                msgs.append(AIMessage(content=h["content"]))
        msgs.append(HumanMessage(content=question))
        return msgs

    def generate(self, question: str, context: str, history: list[dict] = None) -> str:
        try:
            msgs = self._build_messages(question, context, history or [])
            result = self._llm.invoke(msgs)
            return result.content
        except openai.RateLimitError:
            raise RuntimeError("OpenAI quota exceeded. Please try again later.")
        except openai.APIError as exc:
            raise RuntimeError(f"OpenAI service error: {exc}") from exc

    def stream(self, question: str, context: str, history: list[dict] = None) -> Iterator[str]:
        try:
            msgs = self._build_messages(question, context, history or [])
            for chunk in self._llm.stream(msgs):
                if chunk.content:
                    yield chunk.content
        except openai.RateLimitError:
            raise RuntimeError("OpenAI quota exceeded. Please try again later.")
        except openai.APIError as exc:
            raise RuntimeError(f"OpenAI service error: {exc}") from exc
