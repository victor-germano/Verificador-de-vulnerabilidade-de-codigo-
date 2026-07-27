import uuid
from datetime import UTC, datetime, timedelta
from enum import StrEnum

from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import get_settings
from app.core.exceptions import AuthenticationError

settings = get_settings()


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenPayload(BaseModel):
    sub: str
    type: TokenType
    exp: datetime


def _create_token(subject: uuid.UUID, token_type: TokenType, expires_delta: timedelta) -> str:
    now = datetime.now(UTC)
    payload = {"sub": str(subject), "type": token_type.value, "exp": now + expires_delta}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: uuid.UUID) -> str:
    return _create_token(
        subject, TokenType.ACCESS, timedelta(minutes=settings.access_token_expire_minutes)
    )


def create_refresh_token(subject: uuid.UUID) -> str:
    return _create_token(
        subject, TokenType.REFRESH, timedelta(minutes=settings.refresh_token_expire_minutes)
    )


def decode_token(token: str, expected_type: TokenType = TokenType.ACCESS) -> TokenPayload:
    try:
        raw_payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        payload = TokenPayload.model_validate(raw_payload)
    except (JWTError, ValueError) as exc:
        raise AuthenticationError("Invalid or expired token.") from exc

    if payload.type != expected_type:
        raise AuthenticationError("Unexpected token type.")

    return payload
