from pydantic import BaseModel, Field

from app.models.enums import Confidence, Language, Severity


class Rule(BaseModel):
    """Full metadata for one vulnerability rule.

    Loaded from a YAML file in `rules/definitions/`. The `id` is used both
    as the rule's public identifier (shown in findings/reports) and as the
    key under which its detection logic is registered in
    `matcher_registry` (see `rules/matcher_registry.py`).
    """

    id: str
    name: str
    description: str
    category: str
    owasp: str
    cwe: str
    cvss: float
    severity: Severity
    confidence: Confidence = Confidence.MEDIUM
    languages: list[Language]
    message: str
    recommendation: str
    vulnerable_example: str
    secure_example: str
    references: list[str] = Field(default_factory=list)
