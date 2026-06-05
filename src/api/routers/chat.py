import json
import logging
import os
from fastapi import APIRouter, Depends, HTTPException, status

_log = logging.getLogger("growsage.security")
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from src.services.chat_service import ChatService
from src.services.conversation_service import ConversationService
from src.api.deps import get_chat_service, get_current_user, get_db, get_conv_service
from src.domain.models import ChatRequest, ChatResponse, SourceDTO, User
from src.infrastructure.usage_repo import check_and_increment
from src.infrastructure.redis_store import get_cached_response, cache_response

router = APIRouter(prefix="/chat", tags=["chat"])

_DEFAULT_DAILY_LIMIT = 30
_CACHE_CHUNK_SIZE = 40  # chars per simulated streaming token from cache


def _check_verified(user: User) -> None:
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="UNVERIFIED_EMAIL",
        )


def _check_rate_limit(db: Session, user_id: str) -> None:
    limit = int(os.getenv("DAILY_REQUEST_LIMIT", _DEFAULT_DAILY_LIMIT))
    if not check_and_increment(db, user_id, limit):
        _log.warning("DAILY_LIMIT_REACHED user_id=%s", user_id)
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
    _check_verified(current_user)
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

    Responses are cached in Redis for 24 h when history is empty (first message).
    Cache hits stream the stored answer in chunks — same UX, zero OpenAI cost.
    """
    _check_verified(current_user)
    _check_rate_limit(db, current_user.id)

    # Resolve or create conversation
    conversation_id = body.conversation_id
    if conversation_id and not conv_svc.get_conversation(conversation_id, current_user.id):
        conversation_id = None

    if not conversation_id:
        title = body.question[:60].strip() or "New conversation"
        conv = conv_svc.create(user_id=current_user.id, title=title)
        conversation_id = conv.id

    conv_svc.add_message(conversation_id=conversation_id, role="user", content=body.question)

    # Reconstruct history from DB — never trust client-supplied history.
    # Ignore body.history to prevent prompt injection via fabricated context.
    db_messages = conv_svc.get_messages(conversation_id, current_user.id)
    # Exclude the message we just added (last one) — it's the current question
    history = [
        {"role": m.role, "content": m.content}
        for m in db_messages[:-1]
    ]
    use_cache = not history  # only cache context-free questions (new conversation)

    def generate():
        try:
            # ── Cache hit: stream stored answer without calling OpenAI ─────────
            cached = get_cached_response(body.question) if use_cache else None
            if cached:
                yield f"data: {json.dumps({'type': 'sources', 'sources': cached['sources'], 'conversation_id': conversation_id})}\n\n"

                answer = cached["answer"]
                for i in range(0, len(answer), _CACHE_CHUNK_SIZE):
                    chunk = answer[i:i + _CACHE_CHUNK_SIZE]
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"

                msg = conv_svc.add_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=answer,
                    sources=cached["sources"],
                )
                yield f"data: {json.dumps({'type': 'done', 'message_id': msg.id, 'cached': True})}\n\n"
                return

            # ── Cache miss: stream from OpenAI and store result ───────────────
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

            # Store in cache for future identical questions
            if use_cache:
                cache_response(body.question, full_content, sources_dto)

        except RuntimeError as exc:
            # RuntimeError messages are app-controlled (OpenAI quota, service error)
            # Strip anything that could leak internal details beyond known safe messages
            msg = str(exc)
            safe = msg if msg.startswith(("OpenAI", "Daily limit")) else "Service temporarily unavailable"
            yield f"data: {json.dumps({'type': 'error', 'detail': safe})}\n\n"
        except Exception:
            yield f"data: {json.dumps({'type': 'error', 'detail': 'An unexpected error occurred'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
