import uuid

import pytest

from app.core.exceptions import FeatureNotConfiguredError, NotFoundError
from app.models.enums import Confidence, Language, Severity
from app.models.finding import Finding
from app.scanner.ai.analyzer import AIAnalyzer, NullAIAnalyzer
from app.services.ai_service import AIService


class _FakeFindingRepository:
    def __init__(self, by_id: dict | None = None, search_result: list | None = None) -> None:
        self._by_id = by_id or {}
        self._search_result = search_result or []

    async def get_by_id(self, finding_id):
        return self._by_id.get(finding_id)

    async def search(self, filters):
        return self._search_result

    async def bulk_create(self, findings):  # pragma: no cover - unused by AIService
        raise NotImplementedError


class _FakeAIAnalyzer(AIAnalyzer):
    def explain(self, finding) -> str:
        return "explained"

    def suggest_fix(self, finding) -> str:
        return "fixed"

    def summarize(self, findings) -> str:
        return f"summary of {len(findings)}"


def _make_finding(finding_id: uuid.UUID) -> Finding:
    return Finding(
        id=finding_id,
        scan_id=uuid.uuid4(),
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
        references="",
    )


async def test_explain_finding_returns_analyzer_output() -> None:
    finding_id = uuid.uuid4()
    repo = _FakeFindingRepository(by_id={finding_id: _make_finding(finding_id)})
    service = AIService(repo, _FakeAIAnalyzer())
    assert await service.explain_finding(finding_id) == "explained"


async def test_suggest_fix_returns_analyzer_output() -> None:
    finding_id = uuid.uuid4()
    repo = _FakeFindingRepository(by_id={finding_id: _make_finding(finding_id)})
    service = AIService(repo, _FakeAIAnalyzer())
    assert await service.suggest_fix(finding_id) == "fixed"


async def test_explain_finding_raises_not_found_for_unknown_id() -> None:
    service = AIService(_FakeFindingRepository(), _FakeAIAnalyzer())
    with pytest.raises(NotFoundError):
        await service.explain_finding(uuid.uuid4())


async def test_summarize_scan_returns_analyzer_output() -> None:
    repo = _FakeFindingRepository(search_result=[_make_finding(uuid.uuid4())])
    service = AIService(repo, _FakeAIAnalyzer())
    assert await service.summarize_scan(uuid.uuid4()) == "summary of 1"


async def test_explain_finding_translates_not_implemented_to_feature_not_configured() -> None:
    finding_id = uuid.uuid4()
    repo = _FakeFindingRepository(by_id={finding_id: _make_finding(finding_id)})
    service = AIService(repo, NullAIAnalyzer())
    with pytest.raises(FeatureNotConfiguredError):
        await service.explain_finding(finding_id)


async def test_summarize_scan_translates_not_implemented_to_feature_not_configured() -> None:
    repo = _FakeFindingRepository(search_result=[_make_finding(uuid.uuid4())])
    service = AIService(repo, NullAIAnalyzer())
    with pytest.raises(FeatureNotConfiguredError):
        await service.summarize_scan(uuid.uuid4())
