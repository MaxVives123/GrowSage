"""SQLAlchemy setup — ORM models + engine/session factory."""
from __future__ import annotations
import os
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, DateTime, Integer, ForeignKey, Text, create_engine, Index
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

Base = declarative_base()


class UserORM(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class UsageORM(Base):
    __tablename__ = "usage"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    date = Column(String, primary_key=True)  # ISO date "YYYY-MM-DD"
    request_count = Column(Integer, default=0, nullable=False)


class ConversationORM(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class MessageORM(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String, nullable=False)        # "user" | "assistant"
    content = Column(Text, nullable=False)
    sources_json = Column(Text, default="[]")   # JSON list of SourceDTO dicts
    created_at = Column(DateTime, default=datetime.utcnow)


class FeedbackORM(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String, ForeignKey("messages.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)    # 1 or -1
    created_at = Column(DateTime, default=datetime.utcnow)


class EmailVerificationTokenORM(Base):
    """DB fallback for email verification tokens when Redis is unavailable."""
    __tablename__ = "email_verification_tokens"

    token = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)

    __table_args__ = (Index("ix_evt_user_id", "user_id"),)


def make_engine(db_url: str | None = None):
    url = db_url or os.getenv("DATABASE_URL", "sqlite:///./growsage.db")
    if url.startswith("sqlite"):
        is_uri = "uri=true" in url or "mode=memory" in url
        kwargs: dict = {"check_same_thread": False}
        if is_uri:
            kwargs["uri"] = True
    else:
        kwargs = {}
    return create_engine(url, connect_args=kwargs)


def make_session_factory(db_url: str | None = None):
    engine = make_engine(db_url)
    Base.metadata.create_all(engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
