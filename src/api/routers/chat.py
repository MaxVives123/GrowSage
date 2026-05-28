import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.services.chat_service import ChatService
from src.api.deps import get_chat_service, get_current_user, get_db
from src.domain.models import ChatRequest, ChatResponse, SourceDTO, User
from src.infrastructure.usage_repo import check_and_increment

router = APIRouter(prefix="/chat", tags=["chat"])

_DEFAULT_DAILY_LIMIT = 30


@router.post("", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    svc: ChatService = Depends(get_chat_service),
    db: Session = Depends(get_db),
):
    limit = int(os.getenv("DAILY_REQUEST_LIMIT", _DEFAULT_DAILY_LIMIT))
    if not check_and_increment(db, current_user.id, limit):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily limit of {limit} messages reached. Try again tomorrow.",
        )
    try:
        result = svc.answer(body.question)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    return ChatResponse(
        answer=result.answer,
        sources=[SourceDTO(name=s.source, page=f"p.{s.page}") for s in result.sources],
    )
