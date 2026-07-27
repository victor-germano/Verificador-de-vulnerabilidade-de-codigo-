from app.models.finding import Finding
from app.scanner.engines.analyzer import DetectedFinding


def to_detected_finding(finding: Finding) -> DetectedFinding:
    """Maps a persisted `Finding` row back to the engine-level
    `DetectedFinding` shape - used wherever a service needs to feed a
    stored finding back through `scanner/` code (report generation, AI
    analysis) that only knows about `DetectedFinding`, not the ORM model."""
    return DetectedFinding(
        rule_id=finding.rule_id,
        rule_name=finding.rule_name,
        category=finding.category,
        severity=finding.severity,
        confidence=finding.confidence,
        language=finding.language,
        owasp=finding.owasp or "",
        cwe=finding.cwe or "",
        cvss=finding.cvss or 0.0,
        file_path=finding.file_path,
        line_start=finding.line_start,
        line_end=finding.line_end,
        code_snippet=finding.code_snippet,
        description=finding.description,
        explanation=finding.explanation,
        impact=finding.impact,
        recommendation=finding.recommendation,
        secure_example=finding.secure_example,
        references=[line for line in (finding.references or "").splitlines() if line.strip()],
    )
