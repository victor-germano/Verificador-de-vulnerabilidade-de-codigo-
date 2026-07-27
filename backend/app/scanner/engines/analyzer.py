from dataclasses import dataclass, field

from app.models.enums import Confidence, Language, Severity
from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult
from app.scanner.rules.schema import Rule

_IMPACT_BY_SEVERITY: dict[Severity, str] = {
    Severity.CRITICAL: (
        "Exploração pode levar a comprometimento total do sistema, execução de "
        "código remoto ou vazamento massivo de dados sensíveis."
    ),
    Severity.HIGH: (
        "Exploração pode comprometer a confidencialidade ou integridade de dados "
        "sensíveis, ou permitir acesso não autorizado a funcionalidades restritas."
    ),
    Severity.MEDIUM: (
        "Exploração pode expor informações sensíveis ou permitir manipulação "
        "limitada do comportamento da aplicação."
    ),
    Severity.LOW: (
        "Impacto restrito em um cenário isolado, mas ainda representa um desvio "
        "de boas práticas de segurança que pode agravar outras falhas."
    ),
    Severity.INFO: (
        "Achado informativo, sem exploração direta conhecida, mas relevante para "
        "a postura geral de segurança do projeto."
    ),
}


@dataclass(frozen=True)
class DetectedFinding:
    """Engine-level representation of one detected vulnerability - the
    payload `ScanService` persists as a `Finding` row and reports render."""

    rule_id: str
    rule_name: str
    category: str
    severity: Severity
    confidence: Confidence
    language: Language
    owasp: str
    cwe: str
    cvss: float
    file_path: str
    line_start: int
    line_end: int
    code_snippet: str
    description: str
    explanation: str
    impact: str
    recommendation: str
    secure_example: str
    references: list[str] = field(default_factory=list)


class Analyzer:
    """Turns raw (Rule, MatchResult) detections into fully-described
    `DetectedFinding`s, deduplicating repeated hits of the same rule at the
    same location (e.g. a rule matching both a call and a nested call)."""

    def build_findings(
        self, detections: list[tuple[Rule, MatchResult]], parsed: ParsedFile
    ) -> list[DetectedFinding]:
        findings: list[DetectedFinding] = []
        seen: set[tuple[str, int]] = set()

        for rule, match in detections:
            key = (rule.id, match.line_start)
            if key in seen:
                continue
            seen.add(key)

            findings.append(
                DetectedFinding(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    confidence=match.confidence or rule.confidence,
                    language=parsed.language,
                    owasp=rule.owasp,
                    cwe=rule.cwe,
                    cvss=rule.cvss,
                    file_path=str(parsed.path),
                    line_start=match.line_start,
                    line_end=match.line_end,
                    code_snippet=match.snippet,
                    description=rule.description.strip(),
                    explanation=rule.message.strip(),
                    impact=_IMPACT_BY_SEVERITY[rule.severity],
                    recommendation=rule.recommendation.strip(),
                    secure_example=rule.secure_example.strip(),
                    references=list(rule.references),
                )
            )
        return findings
