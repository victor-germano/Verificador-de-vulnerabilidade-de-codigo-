import uuid

import pytest

from app.core.exceptions import AuthenticationError
from app.security.jwt import TokenType, create_access_token, create_refresh_token, decode_token
from app.security.password import hash_password, verify_password


def test_password_hash_and_verify_roundtrip() -> None:
    hashed = hash_password("correct-horse-battery-staple")
    assert hashed != "correct-horse-battery-staple"
    assert verify_password("correct-horse-battery-staple", hashed)
    assert not verify_password("wrong-password", hashed)


def test_access_token_roundtrip() -> None:
    user_id = uuid.uuid4()
    token = create_access_token(user_id)
    payload = decode_token(token, expected_type=TokenType.ACCESS)
    assert payload.sub == str(user_id)
    assert payload.type == TokenType.ACCESS


def test_refresh_token_roundtrip() -> None:
    user_id = uuid.uuid4()
    token = create_refresh_token(user_id)
    payload = decode_token(token, expected_type=TokenType.REFRESH)
    assert payload.sub == str(user_id)
    assert payload.type == TokenType.REFRESH


def test_decode_token_rejects_wrong_type() -> None:
    token = create_access_token(uuid.uuid4())
    with pytest.raises(AuthenticationError):
        decode_token(token, expected_type=TokenType.REFRESH)


def test_decode_token_rejects_garbage() -> None:
    with pytest.raises(AuthenticationError):
        decode_token("not-a-real-token", expected_type=TokenType.ACCESS)
