import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import ScanStatus, ScanTargetType


class ScanCreateRequest(BaseModel):
    project_id: uuid.UUID
    target_type: ScanTargetType
    target_reference: str


class GitScanRequest(BaseModel):
    project_id: uuid.UUID
    repository_url: str = Field(min_length=1, max_length=2000)
    access_token: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
        description=(
            "Personal access token for private repositories. Used only for "
            "this single clone (via an http.extraheader override) - never "
            "stored; only `repository_url` is persisted on the Scan record."
        ),
    )

    @field_validator("repository_url")
    @classmethod
    def _require_http_scheme(cls, value: str) -> str:
        if not value.startswith(("https://", "http://")):
            raise ValueError("repository_url must start with http:// or https://")
        return value


class ScanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    target_type: ScanTargetType
    target_reference: str
    status: ScanStatus
    files_scanned: int
    security_score: int | None
    started_at: datetime | None
    finished_at: datetime | None
    duration_ms: int | None
    error_message: str | None
    created_at: datetime
