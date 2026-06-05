from fastapi import APIRouter, Depends, HTTPException, status
from src.api.deps import get_current_user, get_conv_service
from src.domain.models import ConversationDTO, MessageDTO, SourceDTO, FeedbackRequest, User
from src.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationDTO])
def list_conversations(
    current_user: User = Depends(get_current_user),
    svc: ConversationService = Depends(get_conv_service),
):
    convs = svc.list_by_user(current_user.id)
    return [
        ConversationDTO(id=c.id, title=c.title, created_at=c.created_at, updated_at=c.updated_at)
        for c in convs
    ]


@router.get("/{conversation_id}/messages", response_model=list[MessageDTO])
def get_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    svc: ConversationService = Depends(get_conv_service),
):
    try:
        messages = svc.get_messages(conversation_id, current_user.id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return [
        MessageDTO(
            id=m.id,
            conversation_id=m.conversation_id,
            role=m.role,
            content=m.content,
            sources=[SourceDTO(**s) for s in m.sources],
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    svc: ConversationService = Depends(get_conv_service),
):
    try:
        svc.delete(conversation_id, current_user.id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")


@router.post("/messages/{message_id}/feedback", status_code=status.HTTP_204_NO_CONTENT)
def submit_feedback(
    message_id: str,
    body: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    svc: ConversationService = Depends(get_conv_service),
):
    try:
        svc.add_feedback(message_id=message_id, user_id=current_user.id, rating=body.rating)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
