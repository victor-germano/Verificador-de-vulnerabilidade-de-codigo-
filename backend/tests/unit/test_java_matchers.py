from pathlib import Path

from app.scanner.parsers.java_parser import JavaParser
from app.scanner.rules import matchers as _matchers  # noqa: F401 - registers matchers
from app.scanner.rules.matcher_registry import get_matcher

_parser = JavaParser()


def _matches(rule_id: str, source: str) -> list:
    parsed = _parser.parse(Path("Sample.java"), source)
    matcher = get_matcher(rule_id)
    assert matcher is not None
    return matcher(parsed)


def test_java_sql_injection_flags_concatenated_query() -> None:
    vulnerable = """
    class Foo {
      void bar(String id) {
        stmt.executeQuery("SELECT * FROM users WHERE id = " + id);
      }
    }
    """
    assert len(_matches("JAVASQL001", vulnerable)) == 1


def test_java_sql_injection_ignores_literal_query() -> None:
    safe = """
    class Foo {
      void bar() {
        stmt.executeQuery("SELECT * FROM users");
      }
    }
    """
    assert _matches("JAVASQL001", safe) == []


def test_java_command_injection_flags_dynamic_argument() -> None:
    vulnerable = """
    class Foo {
      void bar(String cmd) {
        Runtime.getRuntime().exec(cmd);
      }
    }
    """
    assert len(_matches("JAVACMD001", vulnerable)) == 1


def test_java_command_injection_ignores_literal_argument() -> None:
    safe = """
    class Foo {
      void bar() {
        Runtime.getRuntime().exec("ls");
      }
    }
    """
    assert _matches("JAVACMD001", safe) == []
