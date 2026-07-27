from pathlib import Path

from app.scanner.parsers.csharp_parser import CSharpParser
from app.scanner.rules import matchers as _matchers  # noqa: F401 - registers matchers
from app.scanner.rules.matcher_registry import get_matcher

_parser = CSharpParser()


def _matches(rule_id: str, source: str) -> list:
    parsed = _parser.parse(Path("Sample.cs"), source)
    matcher = get_matcher(rule_id)
    assert matcher is not None
    return matcher(parsed)


def test_csharp_sql_injection_flags_concatenated_command() -> None:
    vulnerable = """
    class Foo {
      void Bar(string id, SqlConnection conn) {
        var cmd = new SqlCommand("SELECT * FROM users WHERE id = " + id, conn);
      }
    }
    """
    assert len(_matches("CSHARPSQL001", vulnerable)) == 1


def test_csharp_sql_injection_ignores_literal_command() -> None:
    safe = """
    class Foo {
      void Bar(SqlConnection conn) {
        var cmd = new SqlCommand("SELECT * FROM users", conn);
      }
    }
    """
    assert _matches("CSHARPSQL001", safe) == []


def test_csharp_command_injection_flags_dynamic_argument() -> None:
    vulnerable = """
    class Foo {
      void Baz(string host) {
        Process.Start("ping", host);
      }
    }
    """
    assert len(_matches("CSHARPCMD001", vulnerable)) == 1


def test_csharp_command_injection_ignores_literal_arguments() -> None:
    safe = """
    class Foo {
      void Baz() {
        Process.Start("ping", "-c");
      }
    }
    """
    assert _matches("CSHARPCMD001", safe) == []
