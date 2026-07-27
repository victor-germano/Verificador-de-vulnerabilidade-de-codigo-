from pathlib import Path

from app.scanner.parsers.rust_parser import RustParser
from app.scanner.rules import matchers as _matchers  # noqa: F401 - registers matchers
from app.scanner.rules.matcher_registry import get_matcher

_parser = RustParser()


def _matches(rule_id: str, source: str) -> list:
    parsed = _parser.parse(Path("sample.rs"), source)
    matcher = get_matcher(rule_id)
    assert matcher is not None
    return matcher(parsed)


def test_rust_sql_injection_flags_format_macro_query() -> None:
    vulnerable = """
    fn f(id: &str) {
        conn.execute(&format!("SELECT * FROM users WHERE id = {}", id), []);
    }
    """
    assert len(_matches("RUSTSQL001", vulnerable)) == 1


def test_rust_sql_injection_ignores_placeholder_query() -> None:
    safe = """
    fn f(id: &str) {
        conn.execute("SELECT * FROM users WHERE id = ?1", params![id]);
    }
    """
    assert _matches("RUSTSQL001", safe) == []


def test_rust_command_injection_flags_dynamic_argument() -> None:
    vulnerable = """
    fn f(cmd: &str) {
        Command::new(cmd).spawn();
    }
    """
    assert len(_matches("RUSTCMD001", vulnerable)) == 1


def test_rust_command_injection_ignores_literal_argument() -> None:
    safe = """
    fn f() {
        Command::new("ping").spawn();
    }
    """
    assert _matches("RUSTCMD001", safe) == []
