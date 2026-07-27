from pathlib import Path

import pytest

from app.models.enums import Confidence, Language, Severity
from app.scanner.engines.analyzer import Analyzer, DetectedFinding
from app.scanner.engines.detector import Detector
from app.scanner.engines.risk_calculator import RiskCalculator
from app.scanner.engines.rule_engine import RuleEngine
from app.scanner.engines.scanner import ScannerEngine
from app.scanner.parsers.python_parser import PythonParser


def test_rule_engine_filters_rules_by_language() -> None:
    engine = RuleEngine()
    python_rules = engine.rules_for_language(Language.PYTHON)
    java_rules = engine.rules_for_language(Language.JAVA)

    assert any(r.id == "SQL001" for r in python_rules)
    assert not any(r.id == "SQL001" for r in java_rules)  # AST-only rule
    assert any(r.id == "SECRET001" for r in java_rules)  # generic regex rule


def test_rule_engine_get_rule_returns_none_for_unknown_id() -> None:
    engine = RuleEngine()
    assert engine.get_rule("DOES_NOT_EXIST") is None
    assert engine.get_rule("SQL001") is not None


def test_detector_runs_applicable_rules_and_skips_unmatched() -> None:
    parser = PythonParser()
    parsed = parser.parse(Path("sample.py"), "eval(user_input)\n")
    detector = Detector(RuleEngine())

    detections = detector.detect(parsed)

    assert any(rule.id == "CODE001" for rule, _ in detections)


def test_analyzer_deduplicates_same_rule_and_line() -> None:
    parser = PythonParser()
    parsed = parser.parse(Path("sample.py"), "eval(user_input)\n")
    detector = Detector(RuleEngine())
    analyzer = Analyzer()

    detections = detector.detect(parsed)
    findings = analyzer.build_findings(detections, parsed)
    findings_again = analyzer.build_findings(detections + detections, parsed)

    assert len(findings) == len(findings_again)  # duplicates collapsed


def test_analyzer_populates_all_required_fields() -> None:
    parser = PythonParser()
    parsed = parser.parse(Path("sample.py"), "eval(user_input)\n")
    detector = Detector(RuleEngine())
    analyzer = Analyzer()

    findings = analyzer.build_findings(detector.detect(parsed), parsed)
    assert len(findings) == 1
    finding = findings[0]

    for field in (
        finding.description,
        finding.explanation,
        finding.impact,
        finding.recommendation,
        finding.secure_example,
    ):
        assert field and isinstance(field, str)


@pytest.fixture
def sample_finding_factory():
    def _make(severity: Severity) -> DetectedFinding:
        return DetectedFinding(
            rule_id="TEST001",
            rule_name="Test Rule",
            category="Test",
            severity=severity,
            confidence=Confidence.HIGH,
            language=Language.PYTHON,
            owasp="A00",
            cwe="CWE-0",
            cvss=5.0,
            file_path="a.py",
            line_start=1,
            line_end=1,
            code_snippet="x = 1",
            description="d",
            explanation="e",
            impact="i",
            recommendation="r",
            secure_example="s",
            references=[],
        )

    return _make


def test_risk_calculator_returns_100_with_no_findings() -> None:
    assert RiskCalculator().calculate([], files_scanned=10) == 100


def test_risk_calculator_penalizes_critical_more_than_low(sample_finding_factory) -> None:
    calculator = RiskCalculator()
    critical_score = calculator.calculate(
        [sample_finding_factory(Severity.CRITICAL)], files_scanned=1
    )
    low_score = calculator.calculate([sample_finding_factory(Severity.LOW)], files_scanned=1)
    assert critical_score < low_score


def test_risk_calculator_score_stays_within_bounds(sample_finding_factory) -> None:
    calculator = RiskCalculator()
    many_findings = [sample_finding_factory(Severity.CRITICAL) for _ in range(50)]
    score = calculator.calculate(many_findings, files_scanned=1)
    assert 0 <= score <= 100


def test_scanner_engine_scans_a_single_file(tmp_path) -> None:
    target = tmp_path / "vulnerable.py"
    target.write_text("eval(user_input)\n", encoding="utf-8")

    result = ScannerEngine().scan_path(target)

    assert result.files_scanned == 1
    assert any(f.rule_id == "CODE001" for f in result.findings)
    assert result.security_score < 100


def test_scanner_engine_scans_a_directory_and_skips_ignored_dirs(tmp_path) -> None:
    (tmp_path / "app.py").write_text("eval(user_input)\n", encoding="utf-8")
    ignored_dir = tmp_path / "node_modules"
    ignored_dir.mkdir()
    (ignored_dir / "lib.py").write_text("eval(other)\n", encoding="utf-8")

    result = ScannerEngine().scan_path(tmp_path)

    assert result.files_scanned == 1
    assert all("node_modules" not in f.file_path for f in result.findings)


def test_scanner_engine_returns_clean_result_for_safe_code(tmp_path) -> None:
    target = tmp_path / "clean.py"
    target.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")

    result = ScannerEngine().scan_path(target)

    assert result.files_scanned == 1
    assert result.findings == []
    assert result.security_score == 100
