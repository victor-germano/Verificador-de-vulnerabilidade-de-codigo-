import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, enum_values
from app.models.enums import ProjectRole

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class ProjectCollaborator(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A user granted access to someone else's project, with a role. The
    project owner (`Project.owner_id`) is never represented here - they
    always have full access implicitly."""

    __tablename__ = "project_collaborators"
    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_project_collaborator"),)

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    role: Mapped[ProjectRole] = mapped_column(
        Enum(ProjectRole, values_callable=enum_values),
        nullable=False,
        default=ProjectRole.VIEWER,
    )

    project: Mapped["Project"] = relationship(back_populates="collaborators")
    user: Mapped["User"] = relationship()
