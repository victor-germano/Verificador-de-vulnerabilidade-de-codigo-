"""project collaborators (per-project roles: editor, viewer)

Revision ID: 0002_project_collaborators
Revises: 0001_initial
Create Date: 2026-07-27

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_project_collaborators"
down_revision: str | None = "0001_initial"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

project_role_enum = postgresql.ENUM("editor", "viewer", name="projectrole", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    project_role_enum.create(bind, checkfirst=True)

    op.create_table(
        "project_collaborators",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False
        ),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column("role", project_role_enum, nullable=False, server_default="viewer"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("project_id", "user_id", name="uq_project_collaborator"),
    )


def downgrade() -> None:
    op.drop_table("project_collaborators")

    bind = op.get_bind()
    project_role_enum.drop(bind, checkfirst=True)
