"""Domain models — pure Python, zero external dependencies."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from pydantic import BaseModel, field_validator


# ── Domain entities ──────────────────────────────────────────────────────────

@dataclass
class User:
    id: str
    email: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SearchResult:
    content: str
    source: str
    page: str


@dataclass
class ChatAnswer:
    answer: str
    sources: list[SearchResult]


# ── API schemas (Pydantic) ───────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: str
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChatRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def question_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Question cannot be empty")
        return v


class SourceDTO(BaseModel):
    name: str
    page: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceDTO]


class UserDTO(BaseModel):
    id: str
    email: str
    created_at: datetime
