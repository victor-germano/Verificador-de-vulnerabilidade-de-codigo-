import pytest

from app.models.enums import Confidence, Language, Severity
from app.scanner.ai.analyzer import NullAIAnalyzer
from app.scanner.engines.analyzer import DetectedFinding


@pytest.fixture
def finding() -> DetectedFinding:
    return DetectedFinding(
        rule_id="SQL001",
        rule_name="SQL Injection",
        category="Injection",
        severity=Severity.CRITICAL,
        confidence=Confidence.MEDIUM,
        language=Language.PYTHON,
        owasp="A03",
        cwe="CWE-89",
        cvss=9.8,
        file_path="a.py",
        line_start=1,
        line_end=1,
        code_snippet="x",
        description="d",
        explanation="e",
        impact="i",
        recommendation="r",
        secure_example="s",
    )


def test_null_ai_analyzer_raises_not_implemented(finding: DetectedFinding) -> None:
    analyzer = NullAIAnalyzer()
    with pytest.raises(NotImplementedError):
        analyzer.explain(finding)
    with pytest.raises(NotImplementedError):
        analyzer.suggest_fix(finding)
    with pytest.raises(NotImplementedError):
        analyzer.summarize([finding])
