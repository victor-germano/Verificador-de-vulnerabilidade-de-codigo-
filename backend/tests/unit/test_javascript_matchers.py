from pathlib import Path

from app.scanner.parsers.javascript_parser import JavaScriptParser
from app.scanner.rules import matchers as _matchers  # noqa: F401 - registers matchers
from app.scanner.rules.matcher_registry import get_matcher

_parser = JavaScriptParser()


def _matches(rule_id: str, source: str) -> list:
    parsed = _parser.parse(Path("sample.js"), source)
    matcher = get_matcher(rule_id)
    assert matcher is not None
    return matcher(parsed)


def test_unsafe_eval_flags_eval_call() -> None:
    assert len(_matches("JSEVAL001", "eval(userInput);")) == 1


def test_unsafe_eval_flags_settimeout_with_string() -> None:
    assert len(_matches("JSEVAL001", "setTimeout('doSomething()', 1000);")) == 1


def test_unsafe_eval_ignores_settimeout_with_function_ref() -> None:
    assert _matches("JSEVAL001", "setTimeout(doSomething, 1000);") == []


def test_unsafe_eval_flags_new_function() -> None:
    assert len(_matches("JSEVAL001", "const f = new Function('return 1');")) == 1


def test_dom_xss_flags_dynamic_inner_html() -> None:
    assert len(_matches("JSXSS001", "element.innerHTML = userComment;")) == 1


def test_dom_xss_ignores_literal_inner_html() -> None:
    assert _matches("JSXSS001", "element.innerHTML = '<b>fixed</b>';") == []


def test_dom_xss_flags_document_write() -> None:
    assert len(_matches("JSXSS001", "document.write(userComment);")) == 1


def test_command_injection_flags_exec_with_template_string() -> None:
    assert len(_matches("JSCMD001", "exec(`ping ${host}`);")) == 1


def test_command_injection_flags_exec_sync_with_identifier() -> None:
    assert len(_matches("JSCMD001", "execSync(command);")) == 1


def test_command_injection_ignores_exec_with_string_literal() -> None:
    assert _matches("JSCMD001", "exec('ping -c 1 localhost');") == []
