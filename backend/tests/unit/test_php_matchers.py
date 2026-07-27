from pathlib import Path

from app.scanner.parsers.php_parser import PhpParser
from app.scanner.rules import matchers as _matchers  # noqa: F401 - registers matchers
from app.scanner.rules.matcher_registry import get_matcher

_parser = PhpParser()


def _matches(rule_id: str, source: str) -> list:
    parsed = _parser.parse(Path("sample.php"), source)
    matcher = get_matcher(rule_id)
    assert matcher is not None
    return matcher(parsed)


def test_php_sql_injection_flags_concatenated_function_call() -> None:
    vulnerable = '<?php mysqli_query($conn, "SELECT * FROM users WHERE id = " . $id); ?>'
    assert len(_matches("PHPSQL001", vulnerable)) == 1


def test_php_sql_injection_flags_concatenated_method_call() -> None:
    vulnerable = '<?php $conn->query("SELECT * FROM users WHERE id = " . $id); ?>'
    assert len(_matches("PHPSQL001", vulnerable)) == 1


def test_php_sql_injection_ignores_literal_query() -> None:
    safe = '<?php mysqli_query($conn, "SELECT * FROM users"); ?>'
    assert _matches("PHPSQL001", safe) == []


def test_php_command_injection_flags_dynamic_argument() -> None:
    vulnerable = "<?php exec($cmd); ?>"
    assert len(_matches("PHPCMD001", vulnerable)) == 1


def test_php_command_injection_flags_concatenated_argument() -> None:
    vulnerable = '<?php system("ping " . $host); ?>'
    assert len(_matches("PHPCMD001", vulnerable)) == 1


def test_php_command_injection_ignores_literal_argument() -> None:
    safe = '<?php system("ls -la"); ?>'
    assert _matches("PHPCMD001", safe) == []
