import pytest

from app.api.deps import get_ai_analyzer
from app.config.settings import Settings
from app.scanner.ai import AnthropicAIAnalyzer, NullAIAnalyzer


@pytest.fixture(autouse=True)
def _clear_ai_analyzer_cache():
    get_ai_analyzer.cache_clear()
    yield
    get_ai_analyzer.cache_clear()


def test_get_ai_analyzer_returns_null_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.api.deps.get_settings", lambda: Settings(anthropic_api_key=None))
    assert isinstance(get_ai_analyzer(), NullAIAnalyzer)


def test_get_ai_analyzer_returns_anthropic_with_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.api.deps.get_settings", lambda: Settings(anthropic_api_key="sk-test"))
    assert isinstance(get_ai_analyzer(), AnthropicAIAnalyzer)
