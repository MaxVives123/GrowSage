import json
import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from src.services.chat_service import ChatService
from src.services.conversation_service import ConversationService
from src.api.deps import get_chat_service, get_current_user, get_db, get_conv_service
from src.domain.models import ChatRequest, ChatResponse, SourceDTO, User
from src.infrastructure.usage_repo import check_and_increment

router = APIRouter(prefix="/chat", tags=["chat"])

_DEFAULT_DAILY_LIMIT = 30


def _check_rate_limit(db: Session, user_id: str) -> None:
    limit = int(os.getenv("DAILY_REQUEST_LIMIT", _DEFAULT_DAILY_LIMIT))
    if not check_and_increment(db, user_id, limit):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily limit of {limit} messages reached. Try again tomorrow.",
        )


@router.post("", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    svc: ChatService = Depends(get_chat_service),
    db: Session = Depends(get_db),
):
    """Non-streaming endpoint — kept for backward compatibility and integration tests."""
    _check_rate_limit(db, current_user.id)
    history = [h.model_dump() for h in body.history]
    try:
        result = svc.answer(body.question, history)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    return ChatResponse(
        answer=result.answer,
        sources=[SourceDTO(name=s.source, page=f"p.{s.page}") for s in result.sources],
    )


@router.post("/stream")
def chat_stream(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    svc: ChatService = Depends(get_chat_service),
    conv_svc: ConversationService = Depends(get_conv_service),
    db: Session = Depends(get_db),
):
    """Streaming endpoint using Server-Sent Events.

    SSE event protocol:
      data: {"type": "sources",  "sources": [...], "conversation_id": "uuid"}
      data: {"type": "token",    "content": "chunk of text"}
      data: {"type": "done",     "message_id": "uuid"}
      data: {"type": "error",    "detail": "error message"}
    """
    _check_rate_limit(db, current_user.id)
    history = [h.model_dump() for h in body.history]

    # Resolve or create conversation
    conversation_id = body.conversation_id
    if conversation_id and not conv_svc.get_conversation(conversation_id, current_user.id):
        conversation_id = None  # invalid or foreign — start fresh

    if not conversation_id:
        title = (body.question[:60].strip()) or "New conversation"
        conv = conv_svc.create(user_id=current_user.id, title=title)
        conversation_id = conv.id

    # Persist user message before streaming
    conv_svc.add_message(conversation_id=conversation_id, role="user", content=body.question)

    def generate():
        try:
            sources, token_stream = svc.stream_answer(body.question, history)
            sources_dto = [{"name": s.source, "page": f"p.{s.page}"} for s in sources]

            yield f"data: {json.dumps({'type': 'sources', 'sources': sources_dto, 'conversation_id': conversation_id})}\n\n"

            full_content = ""
            for token in token_stream:
                full_content += token
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

            msg = conv_svc.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=full_content,
                sources=sources_dto,
            )
            yield f"data: {json.dumps({'type': 'done', 'message_id': msg.id})}\n\n"

        except RuntimeError as exc:
            yield f"data: {json.dumps({'type': 'error', 'detail': str(exc)})}\n\n"
        except Exception:
            yield f"data: {json.dumps({'type': 'error', 'detail': 'An unexpected error occurred'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
