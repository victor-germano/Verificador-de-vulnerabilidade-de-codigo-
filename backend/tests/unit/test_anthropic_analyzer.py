from types import SimpleNamespace

import pytest

from app.models.enums import Confidence, Language, Severity
from app.scanner.ai.anthropic_analyzer import AnthropicAIAnalyzer
from app.scanner.engines.analyzer import DetectedFinding


class _FakeMessages:
    def __init__(self, text: str) -> None:
        self._text = text

    def create(self, **kwargs):  # noqa: ANN003 - mirrors the Anthropic SDK signature
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=self._text)])


class _FakeClient:
    def __init__(self, text: str) -> None:
        self.messages = _FakeMessages(text)


def _analyzer_with_fake_response(text: str) -> AnthropicAIAnalyzer:
    analyzer = AnthropicAIAnalyzer(api_key="fake-key", model="fake-model")
    analyzer._client = _FakeClient(text)  # avoids a real network call in tests
    return analyzer


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
        code_snippet="cursor.execute(query)",
        description="d",
        explanation="e",
        impact="i",
        recommendation="r",
        secure_example="s",
    )


def test_explain_returns_model_text(finding: DetectedFinding) -> None:
    analyzer = _analyzer_with_fake_response("explicação gerada pelo modelo")
    assert analyzer.explain(finding) == "explicação gerada pelo modelo"


def test_suggest_fix_returns_model_text(finding: DetectedFinding) -> None:
    analyzer = _analyzer_with_fake_response("cursor.execute('...', (x,))")
    assert analyzer.suggest_fix(finding) == "cursor.execute('...', (x,))"


def test_summarize_returns_model_text(finding: DetectedFinding) -> None:
    analyzer = _analyzer_with_fake_response("resumo executivo gerado")
    assert analyzer.summarize([finding]) == "resumo executivo gerado"


def test_summarize_returns_fixed_message_for_empty_findings() -> None:
    analyzer = AnthropicAIAnalyzer(api_key="fake-key", model="fake-model")
    assert "Nenhuma vulnerabilidade" in analyzer.summarize([])
