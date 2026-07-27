from app.scanner.engines.rule_engine import RuleEngine
from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult, get_matcher
from app.scanner.rules.schema import Rule


class Detector:
    """Runs every rule applicable to a file's language against it, via the
    matcher registered for that rule id. A rule with no registered matcher
    (metadata defined but detection not implemented yet) is silently
    skipped - this lets the catalog document more vulnerability types than
    are currently detected without breaking the engine."""

    def __init__(self, rule_engine: RuleEngine) -> None:
        self._rule_engine = rule_engine

    def detect(self, parsed: ParsedFile) -> list[tuple[Rule, MatchResult]]:
        detections: list[tuple[Rule, MatchResult]] = []
        for rule in self._rule_engine.rules_for_language(parsed.language):
            matcher = get_matcher(rule.id)
            if matcher is None:
                continue
            for match in matcher(parsed):
                detections.append((rule, match))
        return detections
