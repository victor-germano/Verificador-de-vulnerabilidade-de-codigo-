import uuid

from app.core.exceptions import AuthenticationError, ConflictError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse
from app.security.jwt import TokenType, create_access_token, create_refresh_token, decode_token
from app.security.password import hash_password, verify_password


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def register(self, email: str, password: str, full_name: str) -> User:
        existing = await self._user_repository.get_by_email(email)
        if existing is not None:
            raise ConflictError("A user with this email already exists.")
        user = User(email=email, hashed_password=hash_password(password), full_name=full_name)
        return await self._user_repository.create(user)

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self._user_repository.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password.")
        if not user.is_active:
            raise AuthenticationError("User is inactive.")
        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token, expected_type=TokenType.REFRESH)
        user_id = uuid.UUID(payload.sub)
        user = await self._user_repository.get_by_id(user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("Invalid refresh token.")
        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )
