from enum import StrEnum


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Confidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Language(StrEnum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    PHP = "php"
    GO = "go"
    RUST = "rust"
    CSHARP = "csharp"


class ScanStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScanTargetType(StrEnum):
    FILE = "file"
    FOLDER = "folder"
    PROJECT = "project"
    GIT_REPOSITORY = "git_repository"


class ProjectRole(StrEnum):
    """Role of a *collaborator* on a project - distinct from the project's
    owner (`Project.owner_id`), who always has full access and isn't
    represented as a `ProjectCollaborator` row. `EDITOR` can run scans and
    view everything; `VIEWER` can only view."""

    EDITOR = "editor"
    VIEWER = "viewer"
