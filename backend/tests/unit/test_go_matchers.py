from pathlib import Path

from app.scanner.parsers.go_parser import GoParser
from app.scanner.rules import matchers as _matchers  # noqa: F401 - registers matchers
from app.scanner.rules.matcher_registry import get_matcher

_parser = GoParser()


def _matches(rule_id: str, source: str) -> list:
    parsed = _parser.parse(Path("sample.go"), source)
    matcher = get_matcher(rule_id)
    assert matcher is not None
    return matcher(parsed)


def test_go_sql_injection_flags_concatenated_query() -> None:
    vulnerable = """
    package main
    func f(id string) {
        db.Query("SELECT * FROM users WHERE id = " + id)
    }
    """
    assert len(_matches("GOSQL001", vulnerable)) == 1


def test_go_sql_injection_ignores_placeholder_query() -> None:
    safe = """
    package main
    func f(id string) {
        db.Query("SELECT * FROM users WHERE id = ?", id)
    }
    """
    assert _matches("GOSQL001", safe) == []


def test_go_command_injection_flags_dynamic_argument() -> None:
    vulnerable = """
    package main
    func f(cmd string) {
        exec.Command("sh", "-c", cmd)
    }
    """
    assert len(_matches("GOCMD001", vulnerable)) == 1


def test_go_command_injection_ignores_literal_arguments() -> None:
    safe = """
    package main
    func f() {
        exec.Command("ping", "-c", "1")
    }
    """
    assert _matches("GOCMD001", safe) == []
