import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.project_collaborator import ProjectCollaborator
    from app.models.scan import Scan
    from app.models.user import User


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    owner: Mapped["User"] = relationship(back_populates="projects")
    scans: Mapped[list["Scan"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    collaborators: Mapped[list["ProjectCollaborator"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
