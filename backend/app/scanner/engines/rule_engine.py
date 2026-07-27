from app.models.enums import Language
from app.scanner.rules import matchers as _matchers  # noqa: F401 - registers all matchers
from app.scanner.rules.loader import get_rules
from app.scanner.rules.schema import Rule


class RuleEngine:
    """Holds the loaded rule catalog and answers "which rules apply to this
    language" for the `Detector`. Matcher functions themselves live in
    `matcher_registry` - this class only deals with rule metadata."""

    def __init__(self) -> None:
        self._rules: list[Rule] = list(get_rules())

    @property
    def all_rules(self) -> list[Rule]:
        return self._rules

    def rules_for_language(self, language: Language) -> list[Rule]:
        return [rule for rule in self._rules if language in rule.languages]

    def get_rule(self, rule_id: str) -> Rule | None:
        return next((r for r in self._rules if r.id == rule_id), None)
