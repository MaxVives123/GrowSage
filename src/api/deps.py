"""Dependency injection — wires infrastructure into API handlers."""
from __future__ import annotations
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.infrastructure.database import make_session_factory
from src.infrastructure.user_repo import SQLUserRepository
from src.infrastructure.chroma_store import ChromaVectorStore
from src.infrastructure.openai_llm import OpenAILLM
from src.services.auth_service import AuthService
from src.services.chat_service import ChatService
from src.services.conversation_service import ConversationService
from src.domain.models import User

_bearer = HTTPBearer()

# Module-level singletons (overridable in tests)
_session_factory = None
_chat_service: ChatService | None = None


def get_session_factory():
    global _session_factory
    if _session_factory is None:
        _session_factory = make_session_factory()
    return _session_factory


def get_db() -> Session:
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(user_repo=SQLUserRepository(db), db=db)


def get_chat_service() -> ChatService:
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService(
            vector_store=ChromaVectorStore(),
            llm=OpenAILLM(),
        )
    return _chat_service


def get_conv_service(db: Session = Depends(get_db)) -> ConversationService:
    from src.infrastructure.conversation_repo import SQLConversationRepository
    return ConversationService(SQLConversationRepository(db))


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    auth = AuthService(user_repo=SQLUserRepository(db), db=db)
    user = auth.get_user_from_token(credentials.credentials)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
