from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from src.vectorstore import get_retriever


SYSTEM_PROMPT = """Eres un experto en horticultura y cultivo de plantas comestibles.
Usa ÚNICAMENTE la información del contexto proporcionado para responder.
Si la respuesta no está en el contexto, dilo claramente y sugiere qué tipo de fuente podría tener esa información.
Responde en español, de forma práctica y directa.

Contexto:
{context}
"""


def format_docs(docs: list) -> str:
    parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "desconocida")
        parts.append(f"[Fuente {i}: {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def build_chain():
    retriever = get_retriever(k=5)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ])

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


def ask(question: str, chain=None) -> str:
    if chain is None:
        chain = build_chain()
    return chain.invoke(question)
