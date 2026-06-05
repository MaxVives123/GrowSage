"""SQLAlchemy implementation of IUserRepository."""
from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from src.domain.interfaces import IUserRepository
from src.domain.models import User
from .database import UserORM


class SQLUserRepository(IUserRepository):
    def __init__(self, session: Session) -> None:
        self._db = session

    def get_by_email(self, email: str) -> User | None:
        row = self._db.query(UserORM).filter(UserORM.email == email).first()
        return self._to_domain(row) if row else None

    def get_by_id(self, user_id: str) -> User | None:
        row = self._db.query(UserORM).filter(UserORM.id == user_id).first()
        return self._to_domain(row) if row else None

    def create(self, email: str, hashed_password: str, email_verified: bool = False) -> User:
        row = UserORM(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password=hashed_password,
            email_verified=email_verified,
            created_at=datetime.utcnow(),
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return self._to_domain(row)

    def verify_email(self, user_id: str) -> None:
        row = self._db.query(UserORM).filter(UserORM.id == user_id).first()
        if row:
            row.email_verified = True
            self._db.commit()

    @staticmethod
    def _to_domain(row: UserORM) -> User:
        return User(
            id=row.id,
            email=row.email,
            hashed_password=row.hashed_password,
            is_active=row.is_active,
            email_verified=getattr(row, "email_verified", False),
            created_at=row.created_at,
        )
