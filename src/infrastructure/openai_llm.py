"""OpenAI/LangChain adapter — implements ILLM."""
from __future__ import annotations
import openai
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.domain.interfaces import ILLM

_SYSTEM = """You are an expert in horticulture and edible plant cultivation.
Use ONLY the information from the provided context to answer.
If the answer is not in the context, say so clearly and suggest where to look.
Answer in the same language as the question. Be practical and direct.

Context:
{context}
"""


class OpenAILLM(ILLM):
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.2) -> None:
        prompt = ChatPromptTemplate.from_messages([
            ("system", _SYSTEM),
            ("human", "{question}"),
        ])
        self._chain = prompt | ChatOpenAI(model=model, temperature=temperature) | StrOutputParser()

    def generate(self, question: str, context: str) -> str:
        try:
            return self._chain.invoke({"question": question, "context": context})
        except openai.RateLimitError:
            raise RuntimeError("OpenAI quota exceeded. Please try again later.")
        except openai.APIError as exc:
            raise RuntimeError(f"OpenAI service error: {exc}") from exc
