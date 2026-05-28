"""Auth use case — register and login users, issue JWT tokens."""
from __future__ import annotations
from datetime import datetime, timedelta
import os
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
    return key


class AuthService:
    def __init__(self, user_repo: IUserRepository) -> None:
        self._repo = user_repo

    def register(self, email: str, password: str) -> User:
        if self._repo.get_by_email(email):
            raise ValueError(f"Email already registered: {email}")
        return self._repo.create(email=email, hashed_password=_pwd_ctx.hash(password))

    def login(self, email: str, password: str) -> str:
        """Returns a JWT access token or raises ValueError."""
        user = self._repo.get_by_email(email)
        if not user or not _pwd_ctx.verify(password, user.hashed_password):
            raise ValueError("Invalid credentials")
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
            {"sub": user.id, "email": user.email, "exp": expire},
            _secret(),
            algorithm=_ALGORITHM,
        )
