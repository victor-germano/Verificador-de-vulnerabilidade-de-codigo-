from pathlib import Path

from app.scanner.parsers.python_parser import PythonParser
from app.scanner.rules import matchers as _matchers  # noqa: F401 - registers matchers
from app.scanner.rules.matcher_registry import get_matcher

_parser = PythonParser()


def _matches(rule_id: str, source: str) -> list:
    parsed = _parser.parse(Path("sample.py"), source)
    matcher = get_matcher(rule_id)
    assert matcher is not None
    return matcher(parsed)


def test_hardcoded_password_flags_literal_assignment() -> None:
    assert len(_matches("SECRET001", 'password = "SuperSecreta123!"\n')) == 1


def test_hardcoded_password_ignores_placeholder_value() -> None:
    assert _matches("SECRET001", 'password = "changeme"\n') == []


def test_hardcoded_password_ignores_env_lookup() -> None:
    assert _matches("SECRET001", 'password = os.environ["DB_PASSWORD"]\n') == []


def test_hardcoded_secret_flags_api_key_literal() -> None:
    assert len(_matches("SECRET002", 'API_KEY = "sk_live_51Hj29xJd8mQAbCdEfGh"\n')) == 1


def test_hardcoded_secret_ignores_placeholder_value() -> None:
    assert _matches("SECRET002", 'API_KEY = "your-api-key-here"\n') == []


def test_weak_cipher_flags_des_ecb_usage() -> None:
    assert len(_matches("CRYPTO002", "cipher = DES.new(key, DES.MODE_ECB)\n")) >= 1


def test_weak_cipher_ignores_aes_gcm() -> None:
    assert _matches("CRYPTO002", "cipher = AES.new(key, AES.MODE_GCM)\n") == []


def test_sensitive_logging_flags_password_in_log_call() -> None:
    assert len(_matches("LOG001", 'logging.info("login attempt password=%s", password)\n')) == 1


def test_sensitive_logging_ignores_non_sensitive_log_call() -> None:
    assert _matches("LOG001", 'logging.info("login attempt for user_id=%s", user_id)\n') == []


def test_generic_matchers_apply_regardless_of_language() -> None:
    java_parsed = _parser.parse(Path("Config.java"), 'String password = "SuperSecreta123!";\n')
    matcher = get_matcher("SECRET001")
    assert matcher is not None
    assert len(matcher(java_parsed)) == 1
