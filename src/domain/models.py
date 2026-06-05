"""Domain models — pure Python, zero external dependencies."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, field_validator

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


# ── Domain entities ──────────────────────────────────────────────────────────

@dataclass
class User:
    id: str
    email: str
    hashed_password: str
    is_active: bool = True
    email_verified: bool = False
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


@dataclass
class Conversation:
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime


@dataclass
class ChatMessage:
    id: str
    conversation_id: str
    role: str
    content: str
    sources: list
    created_at: datetime


# ── API schemas (Pydantic) ───────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not _EMAIL_RE.match(v):
            raise ValueError("Enter a valid email address")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not v.strip():
            raise ValueError("Password cannot be blank")
        return v


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


_MAX_QUESTION_LEN = 2000    # ~500 tokens
_MAX_HISTORY_TURNS = 20     # 20 exchanges = 40 messages
_MAX_HISTORY_MSG_LEN = 4000 # per message in history


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

    @field_validator("content")
    @classmethod
    def content_not_too_long(cls, v: str) -> str:
        if len(v) > _MAX_HISTORY_MSG_LEN:
            raise ValueError(f"History message too long (max {_MAX_HISTORY_MSG_LEN} chars)")
        return v


class ChatRequest(BaseModel):
    question: str
    conversation_id: str | None = None
    history: list[HistoryMessage] = []

    @field_validator("question")
    @classmethod
    def question_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Question cannot be empty")
        if len(v) > _MAX_QUESTION_LEN:
            raise ValueError(f"Question too long (max {_MAX_QUESTION_LEN} chars)")
        return v

    @field_validator("history")
    @classmethod
    def history_not_too_long(cls, v: list) -> list:
        if len(v) > _MAX_HISTORY_TURNS:
            raise ValueError(f"History too long (max {_MAX_HISTORY_TURNS} messages)")
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
    email_verified: bool
    created_at: datetime


class ConversationDTO(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class MessageDTO(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    sources: list[SourceDTO]
    created_at: datetime


class FeedbackRequest(BaseModel):
    rating: int

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if v not in (1, -1):
            raise ValueError("Rating must be 1 (helpful) or -1 (not helpful)")
        return v
