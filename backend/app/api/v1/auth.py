from fastapi import APIRouter, Depends, Request, status

from app.api.deps import get_auth_service, get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse
from app.security.rate_limiter import limiter
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def register(
    request: Request,
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    user = await auth_service.register(payload.email, payload.password, payload.full_name)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await auth_service.login(payload.email, payload.password)


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("20/minute")
async def refresh(
    request: Request,
    payload: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await auth_service.refresh(payload.refresh_token)
