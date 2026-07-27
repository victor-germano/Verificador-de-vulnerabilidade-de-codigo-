from app.database.base import enum_values
from app.models.enums import Confidence, Language, ScanStatus, ScanTargetType, Severity


def test_enum_values_returns_lowercase_member_values() -> None:
    """Regression test: SQLAlchemy's default for a Python Enum column is to
    persist the member *name* (`"FILE"`), not `.value` (`"file"`). Every
    enum column must pass `values_callable=enum_values` or inserts fail
    against the Postgres native enum types created by Alembic (which use
    the lowercase values) - this only surfaces against real Postgres, not
    the SQLite used in tests, so it's covered here explicitly."""
    assert enum_values(Severity) == ["critical", "high", "medium", "low", "info"]
    assert enum_values(Confidence) == ["high", "medium", "low"]
    assert enum_values(ScanStatus) == ["pending", "running", "completed", "failed"]
    assert enum_values(ScanTargetType) == ["file", "folder", "project", "git_repository"]
    assert "python" in enum_values(Language)
    assert all(value == value.lower() for value in enum_values(Language))
