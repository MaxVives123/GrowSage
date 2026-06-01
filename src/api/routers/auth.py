from fastapi import APIRouter, Depends, HTTPException, Request, status
from src.services.auth_service import AuthService
from src.api.deps import get_auth_service
from src.domain.models import RegisterRequest, LoginRequest, TokenResponse, UserDTO
from src.infrastructure.redis_store import check_ip_limit

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_ip(request: Request) -> str:
    """Extract real client IP, respecting X-Forwarded-For from Railway's proxy."""
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
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts from this IP. Try again in 1 hour.",
        )
    try:
        user = auth.register(body.email, body.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return UserDTO(id=user.id, email=user.email, created_at=user.created_at)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, auth: AuthService = Depends(get_auth_service)):
    try:
        token = auth.login(body.email, body.password)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )
    return TokenResponse(access_token=token)
