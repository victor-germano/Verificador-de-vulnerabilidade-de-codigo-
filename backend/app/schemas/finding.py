import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import Confidence, Language, Severity


class FindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    scan_id: uuid.UUID
    rule_id: str
    rule_name: str
    category: str
    severity: Severity
    confidence: Confidence
    language: Language
    owasp: str | None
    cwe: str | None
    cvss: float | None
    file_path: str
    line_start: int
    line_end: int
    code_snippet: str
    description: str
    explanation: str
    impact: str
    recommendation: str
    secure_example: str
    references: list[str] = []
    created_at: datetime

    @field_validator("references", mode="before")
    @classmethod
    def _split_references(cls, value: str | list[str] | None) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [line for line in value.splitlines() if line.strip()]
        return value
