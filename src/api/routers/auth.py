import logging
import os
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from src.services.auth_service import AuthService
from src.api.deps import get_auth_service, get_current_user
from src.domain.models import RegisterRequest, LoginRequest, TokenResponse, UserDTO, User
from src.infrastructure.redis_store import check_ip_limit

_log = logging.getLogger("growsage.security")

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/register", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
def register(
    body: RegisterRequest,
    request: Request,
    auth: AuthService = Depends(get_auth_service),
):
    ip = _get_ip(request)
    if not check_ip_limit(ip, max_attempts=5, window_seconds=3600):
        _log.warning("REGISTER_RATE_LIMITED ip=%s", ip)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts from this IP. Try again in 1 hour.",
        )
    try:
        user = auth.register(body.email, body.password)
        _log.info("REGISTER_OK email=%s ip=%s", user.email, ip)
    except ValueError as exc:
        _log.warning("REGISTER_CONFLICT email=%s ip=%s", body.email, ip)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return UserDTO(id=user.id, email=user.email, email_verified=user.email_verified, created_at=user.created_at)


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    request: Request,
    auth: AuthService = Depends(get_auth_service),
):
    ip = _get_ip(request)
    if not check_ip_limit(ip, max_attempts=10, window_seconds=900, key_prefix="login"):
        _log.warning("LOGIN_RATE_LIMITED ip=%s email=%s", ip, body.email)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts from this IP. Try again in 15 minutes.",
        )
    try:
        token = auth.login(body.email, body.password)
        _log.info("LOGIN_OK email=%s ip=%s", body.email, ip)
    except ValueError:
        _log.warning("LOGIN_FAILED email=%s ip=%s", body.email, ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return TokenResponse(access_token=token)


@router.get("/verify/{token}", tags=["auth"])
def verify_email(token: str, auth: AuthService = Depends(get_auth_service)):
    """Email verification link — called by clicking the link in the email."""
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    user = auth.verify_email(token)
    if not user:
        return RedirectResponse(f"{frontend_url}?verified=error", status_code=302)
    return RedirectResponse(f"{frontend_url}?verified=success", status_code=302)


@router.post("/resend-verification", status_code=status.HTTP_204_NO_CONTENT)
def resend_verification(
    current_user: User = Depends(get_current_user),
    auth: AuthService = Depends(get_auth_service),
):
    """Resend the verification email (max 3 times per hour)."""
    if current_user.email_verified:
        return  # already verified, nothing to do
    ok = auth.resend_verification(current_user)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many resend attempts. Please wait 1 hour.",
        )
