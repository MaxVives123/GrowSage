"""SQLAlchemy implementation of IConversationRepository."""
from __future__ import annotations
import json
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from src.domain.interfaces import IConversationRepository
from src.domain.models import Conversation, ChatMessage
from src.infrastructure.database import ConversationORM, MessageORM, FeedbackORM


class SQLConversationRepository(IConversationRepository):
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, user_id: str, title: str) -> Conversation:
        row = ConversationORM(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title[:120] or "New conversation",
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return self._conv(row)

    def get_by_id(self, conversation_id: str) -> Conversation | None:
        row = self._db.get(ConversationORM, conversation_id)
        return self._conv(row) if row else None

    def list_by_user(self, user_id: str) -> list[Conversation]:
        rows = (
            self._db.query(ConversationORM)
            .filter(ConversationORM.user_id == user_id)
            .order_by(ConversationORM.updated_at.desc())
            .limit(50)
            .all()
        )
        return [self._conv(r) for r in rows]

    def delete(self, conversation_id: str) -> None:
        self._db.query(FeedbackORM).filter(
            FeedbackORM.message_id.in_(
                self._db.query(MessageORM.id).filter(
                    MessageORM.conversation_id == conversation_id
                )
            )
        ).delete(synchronize_session=False)
        self._db.query(MessageORM).filter(
            MessageORM.conversation_id == conversation_id
        ).delete()
        row = self._db.get(ConversationORM, conversation_id)
        if row:
            self._db.delete(row)
        self._db.commit()

    def add_message(
        self, conversation_id: str, role: str, content: str, sources: list
    ) -> ChatMessage:
        msg = MessageORM(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources_json=json.dumps(sources),
        )
        self._db.add(msg)
        # Bump conversation updated_at
        conv = self._db.get(ConversationORM, conversation_id)
        if conv:
            conv.updated_at = datetime.utcnow()
        self._db.commit()
        self._db.refresh(msg)
        return self._msg(msg)

    def get_messages(self, conversation_id: str) -> list[ChatMessage]:
        rows = (
            self._db.query(MessageORM)
            .filter(MessageORM.conversation_id == conversation_id)
            .order_by(MessageORM.created_at.asc())
            .all()
        )
        return [self._msg(r) for r in rows]

    def add_feedback(self, message_id: str, user_id: str, rating: int) -> None:
        existing = (
            self._db.query(FeedbackORM)
            .filter(FeedbackORM.message_id == message_id, FeedbackORM.user_id == user_id)
            .first()
        )
        if existing:
            existing.rating = rating
        else:
            self._db.add(FeedbackORM(
                id=str(uuid.uuid4()),
                message_id=message_id,
                user_id=user_id,
                rating=rating,
            ))
        self._db.commit()

    @staticmethod
    def _conv(row: ConversationORM) -> Conversation:
        return Conversation(
            id=row.id, user_id=row.user_id, title=row.title,
            created_at=row.created_at, updated_at=row.updated_at,
        )

    @staticmethod
    def _msg(row: MessageORM) -> ChatMessage:
        return ChatMessage(
            id=row.id, conversation_id=row.conversation_id,
            role=row.role, content=row.content,
            sources=json.loads(row.sources_json or "[]"),
            created_at=row.created_at,
        )
