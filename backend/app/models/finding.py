import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, enum_values
from app.models.enums import Confidence, Language, Severity

if TYPE_CHECKING:
    from app.models.scan import Scan


class Finding(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "findings"

    scan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("scans.id"))

    rule_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    rule_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[Severity] = mapped_column(
        Enum(Severity, values_callable=enum_values), nullable=False, index=True
    )
    confidence: Mapped[Confidence] = mapped_column(
        Enum(Confidence, values_callable=enum_values), nullable=False
    )
    language: Mapped[Language] = mapped_column(
        Enum(Language, values_callable=enum_values), nullable=False, index=True
    )

    owasp: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cwe: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cvss: Mapped[float | None] = mapped_column(Float, nullable=True)

    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    line_start: Mapped[int] = mapped_column(Integer, nullable=False)
    line_end: Mapped[int] = mapped_column(Integer, nullable=False)
    code_snippet: Mapped[str] = mapped_column(Text, nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    impact: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    secure_example: Mapped[str] = mapped_column(Text, nullable=False)
    references: Mapped[str | None] = mapped_column(Text, nullable=True)  # newline-separated URLs

    scan: Mapped["Scan"] = relationship(back_populates="findings")
