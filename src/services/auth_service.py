"""Auth use case — register and login users, issue JWT tokens."""
from __future__ import annotations
import os
import uuid
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.domain.interfaces import IUserRepository
from src.domain.models import User

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
_ALGORITHM = "HS256"
_TOKEN_EXPIRE_HOURS = 24


def _secret() -> str:
    key = os.getenv("SECRET_KEY", "")
    if not key:
        raise RuntimeError("SECRET_KEY env var is not set")
    if len(key) < 32:
        raise RuntimeError("SECRET_KEY must be at least 32 characters")
    return key


class AuthService:
    def __init__(self, user_repo: IUserRepository, db=None) -> None:
        self._repo = user_repo
        self._db = db  # optional DB session for token fallback when Redis is down

    def register(self, email: str, password: str) -> User:
        email = email.strip().lower()
        if self._repo.get_by_email(email):
            raise ValueError("This email is already registered")

        # AUTO_VERIFY_EMAIL=true skips email verification (used in tests)
        auto_verify = os.getenv("AUTO_VERIFY_EMAIL", "false").lower() == "true"
        user = self._repo.create(
            email=email,
            hashed_password=_pwd_ctx.hash(password),
            email_verified=auto_verify,
        )

        if not auto_verify:
            self._send_verification(user)

        return user

    def _send_verification(self, user: User) -> None:
        from src.infrastructure.redis_store import create_verification_token
        from src.infrastructure.email_service import send_verification_email
        token = create_verification_token(user.id)
        if not token:
            # Redis unavailable — fall back to DB-stored token
            token = self._create_db_token(user.id)
        if token:
            send_verification_email(user.email, token)
        else:
            print(f"[EMAIL] Cannot create verification token for {user.email} (Redis and DB unavailable)")

    def _create_db_token(self, user_id: str) -> str | None:
        if self._db is None:
            return None
        try:
            from src.infrastructure.database import EmailVerificationTokenORM
            token = str(uuid.uuid4())
            expires_at = datetime.utcnow() + timedelta(hours=24)
            self._db.add(EmailVerificationTokenORM(
                token=token, user_id=user_id, expires_at=expires_at
            ))
            self._db.commit()
            return token
        except Exception as exc:
            print(f"[EMAIL] DB token creation failed: {exc}")
            return None

    def verify_email(self, token: str) -> User | None:
        """Consume the token and mark user as verified. Returns user or None."""
        from src.infrastructure.redis_store import consume_verification_token
        user_id = consume_verification_token(token)
        if not user_id:
            # Try DB fallback
            user_id = self._consume_db_token(token)
        if not user_id:
            return None
        self._repo.verify_email(user_id)
        return self._repo.get_by_id(user_id)

    def _consume_db_token(self, token: str) -> str | None:
        if self._db is None:
            return None
        try:
            from src.infrastructure.database import EmailVerificationTokenORM
            row = self._db.get(EmailVerificationTokenORM, token)
            if not row or row.expires_at < datetime.utcnow():
                return None
            user_id = row.user_id
            self._db.delete(row)
            self._db.commit()
            return user_id
        except Exception:
            return None

    def resend_verification(self, user: User) -> bool:
        """Resend verification email (rate-limited). Returns False if rate limit hit."""
        if user.email_verified:
            return True  # nothing to do
        from src.infrastructure.redis_store import check_resend_limit
        if not check_resend_limit(user.id):
            return False
        self._send_verification(user)
        return True

    def login(self, email: str, password: str) -> str:
        """Returns a JWT access token or raises ValueError."""
        email = email.strip().lower()
        user = self._repo.get_by_email(email)
        if not user:
            raise ValueError("No account found with that email")
        if not _pwd_ctx.verify(password, user.hashed_password):
            raise ValueError("Incorrect password")
        if not user.is_active:
            raise ValueError("This account has been disabled")
        return self._issue_token(user)

    def get_user_from_token(self, token: str) -> User | None:
        try:
            payload = jwt.decode(token, _secret(), algorithms=[_ALGORITHM])
            user_id: str | None = payload.get("sub")
            if not user_id:
                return None
            return self._repo.get_by_id(user_id)
        except JWTError:
            return None

    def _issue_token(self, user: User) -> str:
        expire = datetime.utcnow() + timedelta(hours=_TOKEN_EXPIRE_HOURS)
        return jwt.encode(
            {
                "sub": user.id,
                "email": user.email,
                "email_verified": user.email_verified,
                "exp": expire,
            },
            _secret(),
            algorithm=_ALGORITHM,
        )
