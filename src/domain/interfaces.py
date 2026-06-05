"""Abstract ports — define what each layer needs, not how it's done."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterator
from .models import User, SearchResult, Conversation, ChatMessage


class IVectorStore(ABC):
    @abstractmethod
    def search(self, query: str, k: int = 5) -> list[SearchResult]: ...

    @abstractmethod
    def add_documents(self, docs: list, ids: list[str]) -> None: ...


class ILLM(ABC):
    @abstractmethod
    def generate(self, question: str, context: str, history: list[dict] = None) -> str: ...

    @abstractmethod
    def stream(self, question: str, context: str, history: list[dict] = None) -> Iterator[str]: ...


class IUserRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None: ...

    @abstractmethod
    def create(self, email: str, hashed_password: str, email_verified: bool = False) -> User: ...

    @abstractmethod
    def verify_email(self, user_id: str) -> None: ...


class IConversationRepository(ABC):
    @abstractmethod
    def create(self, user_id: str, title: str) -> Conversation: ...

    @abstractmethod
    def get_by_id(self, conversation_id: str) -> Conversation | None: ...

    @abstractmethod
    def list_by_user(self, user_id: str) -> list[Conversation]: ...

    @abstractmethod
    def delete(self, conversation_id: str) -> None: ...

    @abstractmethod
    def add_message(
        self, conversation_id: str, role: str, content: str, sources: list
    ) -> ChatMessage: ...

    @abstractmethod
    def get_messages(self, conversation_id: str) -> list[ChatMessage]: ...

    @abstractmethod
    def add_feedback(self, message_id: str, user_id: str, rating: int) -> None: ...
