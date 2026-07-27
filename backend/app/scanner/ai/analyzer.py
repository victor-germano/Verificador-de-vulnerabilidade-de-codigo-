"""AI augmentation contract.

`DetectedFinding` already carries a rule-driven explanation, impact and fix
recommendation (see `scanner/engines/analyzer.py`); this interface lets a
concrete implementation (`AnthropicAIAnalyzer` - see `anthropic_analyzer.py`)
enrich that same shape with model-generated, context-specific text without
any other layer changing. Callers should type-hint against `AIAnalyzer`,
never against a concrete implementation, and obtain one only via
`api.deps.get_ai_analyzer` (the factory lives there, not here, since
choosing an implementation requires reading app settings - a concern the
framework-agnostic `scanner/` package deliberately doesn't have).
"""

from abc import ABC, abstractmethod

from app.scanner.engines.analyzer import DetectedFinding


class AIAnalyzer(ABC):
    @abstractmethod
    def explain(self, finding: DetectedFinding) -> str:
        """Returns a natural-language explanation of why `finding` is exploitable."""

    @abstractmethod
    def suggest_fix(self, finding: DetectedFinding) -> str:
        """Returns a code suggestion tailored to `finding`'s exact snippet/context."""

    @abstractmethod
    def summarize(self, findings: list[DetectedFinding]) -> str:
        """Returns an executive summary covering a full set of findings."""


class NullAIAnalyzer(AIAnalyzer):
    """Default implementation while no AI provider is integrated.

    Raises rather than silently returning empty text, so callers that
    forget to feature-flag AI-dependent UI find out immediately instead of
    shipping a blank panel.
    """

    _MESSAGE = (
        "AI analysis is not configured yet. Implement AIAnalyzer with a real "
        "provider and wire it in place of NullAIAnalyzer to enable this feature."
    )

    def explain(self, finding: DetectedFinding) -> str:
        raise NotImplementedError(self._MESSAGE)

    def suggest_fix(self, finding: DetectedFinding) -> str:
        raise NotImplementedError(self._MESSAGE)

    def summarize(self, findings: list[DetectedFinding]) -> str:
        raise NotImplementedError(self._MESSAGE)
