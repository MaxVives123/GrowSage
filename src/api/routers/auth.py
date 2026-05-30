from fastapi import APIRouter, Depends, HTTPException, status
from src.services.auth_service import AuthService
from src.api.deps import get_auth_service
from src.domain.models import RegisterRequest, LoginRequest, TokenResponse, UserDTO

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, auth: AuthService = Depends(get_auth_service)):
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
            detail=str(exc),  # surface descriptive message to the client
        )
    return TokenResponse(access_token=token)
