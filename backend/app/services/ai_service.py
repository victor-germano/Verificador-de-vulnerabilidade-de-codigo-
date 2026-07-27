import uuid

from app.core.exceptions import FeatureNotConfiguredError, NotFoundError
from app.models.finding import Finding
from app.repositories.finding_repository import FindingFilter, FindingRepository
from app.scanner.ai import AIAnalyzer
from app.services.finding_mapping import to_detected_finding


class AIService:
    """Thin orchestration layer between the API and `AIAnalyzer`: fetches
    the persisted `Finding`(s), maps them back to `DetectedFinding`, and
    delegates the actual analysis. Whether AI is configured at all is not
    this class's concern - it just calls whatever `AIAnalyzer` it was
    given (see `api.deps.get_ai_analyzer`, which picks `NullAIAnalyzer` or
    `AnthropicAIAnalyzer` based on settings) and translates
    `NullAIAnalyzer`'s `NotImplementedError` into a proper 501 response
    instead of letting it fall through as an unhandled 500."""

    def __init__(self, finding_repository: FindingRepository, analyzer: AIAnalyzer) -> None:
        self._finding_repository = finding_repository
        self._analyzer = analyzer

    async def explain_finding(self, finding_id: uuid.UUID) -> str:
        finding = await self._get_finding_or_404(finding_id)
        return self._call(self._analyzer.explain, to_detected_finding(finding))

    async def suggest_fix(self, finding_id: uuid.UUID) -> str:
        finding = await self._get_finding_or_404(finding_id)
        return self._call(self._analyzer.suggest_fix, to_detected_finding(finding))

    async def summarize_scan(self, scan_id: uuid.UUID) -> str:
        findings = await self._finding_repository.search(FindingFilter(scan_id=scan_id))
        return self._call(self._analyzer.summarize, [to_detected_finding(f) for f in findings])

    async def _get_finding_or_404(self, finding_id: uuid.UUID) -> Finding:
        finding = await self._finding_repository.get_by_id(finding_id)
        if finding is None:
            raise NotFoundError("Finding not found.")
        return finding

    @staticmethod
    def _call(fn, arg):
        try:
            return fn(arg)
        except NotImplementedError as exc:
            raise FeatureNotConfiguredError(str(exc)) from exc
