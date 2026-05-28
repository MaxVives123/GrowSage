"""Abstract ports — define what each layer needs, not how it's done."""
from __future__ import annotations
from abc import ABC, abstractmethod
from .models import User, SearchResult


class IVectorStore(ABC):
    @abstractmethod
    def search(self, query: str, k: int = 5) -> list[SearchResult]: ...

    @abstractmethod
    def add_documents(self, docs: list, ids: list[str]) -> None: ...


class ILLM(ABC):
    @abstractmethod
    def generate(self, question: str, context: str) -> str: ...


class IUserRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None: ...

    @abstractmethod
    def create(self, email: str, hashed_password: str) -> User: ...
