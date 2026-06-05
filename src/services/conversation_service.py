"""Conversation use case — manage chat sessions and their messages."""
from __future__ import annotations
from src.domain.interfaces import IConversationRepository
from src.domain.models import Conversation, ChatMessage


class ConversationService:
    def __init__(self, repo: IConversationRepository) -> None:
        self._repo = repo

    def create(self, user_id: str, title: str) -> Conversation:
        return self._repo.create(user_id=user_id, title=title or "New conversation")

    def get_conversation(self, conversation_id: str, user_id: str) -> Conversation | None:
        """Return conversation only if it belongs to user."""
        conv = self._repo.get_by_id(conversation_id)
        return conv if conv and conv.user_id == user_id else None

    def list_by_user(self, user_id: str) -> list[Conversation]:
        return self._repo.list_by_user(user_id)

    def delete(self, conversation_id: str, user_id: str) -> None:
        conv = self._repo.get_by_id(conversation_id)
        if not conv or conv.user_id != user_id:
            raise ValueError("Conversation not found")
        self._repo.delete(conversation_id)

    def add_message(
        self, conversation_id: str, role: str, content: str, sources: list = None
    ) -> ChatMessage:
        return self._repo.add_message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources=sources or [],
        )

    def get_messages(self, conversation_id: str, user_id: str) -> list[ChatMessage]:
        conv = self._repo.get_by_id(conversation_id)
        if not conv or conv.user_id != user_id:
            raise ValueError("Conversation not found")
        return self._repo.get_messages(conversation_id)

    def add_feedback(self, message_id: str, user_id: str, rating: int) -> None:
        # ValueError propagates to router if message not found or not owned by user
        self._repo.add_feedback(message_id=message_id, user_id=user_id, rating=rating)
