import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import TypeVar

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

_E = TypeVar("_E", bound=PyEnum)


def enum_values(enum_cls: type[_E]) -> list[str]:
    """`values_callable` for `sqlalchemy.Enum(SomeEnum, values_callable=enum_values)`.

    SQLAlchemy's default behavior for a Python `Enum`/`StrEnum` column is to
    persist the member *name* (`"FILE"`), not its *value* (`"file"`) - even
    for `str`-mixed enums. The Postgres native enum types created by our
    Alembic migrations use the lowercase `.value` strings (matching the YAML
    rule definitions and the API's JSON representation), so every enum
    column must pass this to stay consistent with the DB and the API.
    """
    return [member.value for member in enum_cls]


class Base(DeclarativeBase):
    """Declarative base shared by every ORM model."""


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
