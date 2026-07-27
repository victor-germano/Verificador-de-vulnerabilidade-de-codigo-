import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, enum_values
from app.models.enums import ScanStatus, ScanTargetType

if TYPE_CHECKING:
    from app.models.finding import Finding
    from app.models.project import Project


class Scan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "scans"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"))
    target_type: Mapped[ScanTargetType] = mapped_column(
        Enum(ScanTargetType, values_callable=enum_values), nullable=False
    )
    target_reference: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[ScanStatus] = mapped_column(
        Enum(ScanStatus, values_callable=enum_values), default=ScanStatus.PENDING
    )

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    files_scanned: Mapped[int] = mapped_column(Integer, default=0)
    security_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="scans")
    findings: Mapped[list["Finding"]] = relationship(
        back_populates="scan", cascade="all, delete-orphan"
    )
