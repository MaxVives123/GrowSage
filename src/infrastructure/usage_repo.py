"""Per-user daily request quota — check and increment atomically."""
from __future__ import annotations
from datetime import date
from sqlalchemy.orm import Session
from src.infrastructure.database import UsageORM


def check_and_increment(db: Session, user_id: str, limit: int) -> bool:
    """Return True and increment count if under limit, False if limit reached."""
    today = date.today().isoformat()
    row = db.get(UsageORM, (user_id, today))
    if row is None:
        row = UsageORM(user_id=user_id, date=today, request_count=0)
        db.add(row)
    if row.request_count >= limit:
        return False
    row.request_count += 1
    db.commit()
    return True
