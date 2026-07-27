"""initial schema: users, projects, scans, findings

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-26

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

severity_enum = postgresql.ENUM(
    "critical", "high", "medium", "low", "info", name="severity", create_type=False
)
confidence_enum = postgresql.ENUM("high", "medium", "low", name="confidence", create_type=False)
language_enum = postgresql.ENUM(
    "python", "javascript", "typescript", "java", "php", "go", "rust", "csharp",
    name="language", create_type=False,
)
scan_status_enum = postgresql.ENUM(
    "pending", "running", "completed", "failed", name="scanstatus", create_type=False
)
scan_target_type_enum = postgresql.ENUM(
    "file", "folder", "project", "git_repository", name="scantargettype", create_type=False
)


def upgrade() -> None:
    bind = op.get_bind()
    severity_enum.create(bind, checkfirst=True)
    confidence_enum.create(bind, checkfirst=True)
    language_enum.create(bind, checkfirst=True)
    scan_status_enum.create(bind, checkfirst=True)
    scan_target_type_enum.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "scans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("target_type", scan_target_type_enum, nullable=False),
        sa.Column("target_reference", sa.String(500), nullable=False),
        sa.Column("status", scan_status_enum, nullable=False, server_default="pending"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("files_scanned", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("security_score", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.String(2000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "findings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("scan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("scans.id"), nullable=False),
        sa.Column("rule_id", sa.String(50), nullable=False),
        sa.Column("rule_name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("severity", severity_enum, nullable=False),
        sa.Column("confidence", confidence_enum, nullable=False),
        sa.Column("language", language_enum, nullable=False),
        sa.Column("owasp", sa.String(100), nullable=True),
        sa.Column("cwe", sa.String(20), nullable=True),
        sa.Column("cvss", sa.Float(), nullable=True),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("line_start", sa.Integer(), nullable=False),
        sa.Column("line_end", sa.Integer(), nullable=False),
        sa.Column("code_snippet", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("impact", sa.Text(), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("secure_example", sa.Text(), nullable=False),
        sa.Column("references", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_findings_rule_id", "findings", ["rule_id"])
    op.create_index("ix_findings_severity", "findings", ["severity"])
    op.create_index("ix_findings_language", "findings", ["language"])


def downgrade() -> None:
    op.drop_table("findings")
    op.drop_table("scans")
    op.drop_table("projects")
    op.drop_table("users")

    bind = op.get_bind()
    scan_target_type_enum.drop(bind, checkfirst=True)
    scan_status_enum.drop(bind, checkfirst=True)
    language_enum.drop(bind, checkfirst=True)
    confidence_enum.drop(bind, checkfirst=True)
    severity_enum.drop(bind, checkfirst=True)
