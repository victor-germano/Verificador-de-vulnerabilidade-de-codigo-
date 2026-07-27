from app.models.enums import Language
from app.scanner.rules import matchers as _matchers  # noqa: F401 - registers matchers
from app.scanner.rules.loader import get_rules, load_rules
from app.scanner.rules.matcher_registry import get_matcher, registered_rule_ids


def test_load_rules_returns_all_yaml_definitions() -> None:
    rules = load_rules()
    assert len(rules) == 38
    ids = {rule.id for rule in rules}
    assert "SQL001" in ids
    assert "SECRET002" in ids


def test_every_rule_has_a_registered_matcher() -> None:
    rules = load_rules()
    registered = registered_rule_ids()
    for rule in rules:
        assert rule.id in registered, f"{rule.id} has no matcher registered"
        assert get_matcher(rule.id) is not None


def test_get_rules_is_cached_tuple() -> None:
    first = get_rules()
    second = get_rules()
    assert first is second
    assert isinstance(first, tuple)


def test_rule_languages_are_valid_enum_members() -> None:
    for rule in load_rules():
        for language in rule.languages:
            assert isinstance(language, Language)


def test_rule_severity_and_cvss_are_consistent() -> None:
    for rule in load_rules():
        assert 0.0 <= rule.cvss <= 10.0
        assert rule.severity is not None
