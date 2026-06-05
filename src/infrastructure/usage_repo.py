"""Per-user daily request quota — check and increment atomically."""
from __future__ import annotations
from datetime import date
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.infrastructure.database import UsageORM


def check_and_increment(db: Session, user_id: str, limit: int) -> bool:
    """Return True and increment count if under limit, False if limit reached.

    Uses SELECT FOR UPDATE (Postgres) / BEGIN IMMEDIATE (SQLite) to prevent
    concurrent requests from bypassing the daily cap.
    """
    today = date.today().isoformat()

    # Lock the row for the duration of this transaction
    row = (
        db.query(UsageORM)
        .filter(UsageORM.user_id == user_id, UsageORM.date == today)
        .with_for_update()
        .first()
    )
    if row is None:
        row = UsageORM(user_id=user_id, date=today, request_count=0)
        db.add(row)
        db.flush()  # ensure row is visible within this transaction

    if row.request_count >= limit:
        return False

    row.request_count += 1
    db.commit()
    return True
