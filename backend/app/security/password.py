import bcrypt

# Uses the `bcrypt` package directly rather than passlib: passlib is
# unmaintained and its version-detection shim breaks against modern bcrypt
# releases (no `__about__` attribute), which surfaces as a runtime error on
# the very first hash call. bcrypt's own API is a two-liner anyway.


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
