from dataclasses import dataclass, field
from datetime import datetime

from app.scanner.engines.analyzer import DetectedFinding


@dataclass(frozen=True)
class ReportContext:
    """Everything a report generator needs, independent of output format."""

    project_name: str
    scan_id: str
    generated_at: datetime
    files_scanned: int
    security_score: int
    findings: list[DetectedFinding] = field(default_factory=list)

    @property
    def severity_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for finding in self.findings:
            key = finding.severity.value
            counts[key] = counts.get(key, 0) + 1
        return counts
