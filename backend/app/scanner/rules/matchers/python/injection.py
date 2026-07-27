import ast

from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult, register_matcher
from app.scanner.rules.matchers.python._ast_utils import (
    find_calls,
    get_call_name,
    is_dynamic_string,
    match_from_node,
)

_SQL_EXEC_METHODS = {"execute", "executemany"}
_SHELL_EXEC_FUNCS = {
    "os.system",
    "os.popen",
    "subprocess.run",
    "subprocess.call",
    "subprocess.Popen",
    "subprocess.check_call",
    "subprocess.check_output",
}
_EVAL_FUNCS = {"eval", "exec"}


@register_matcher("SQL001")
def match_sql_injection(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for call in find_calls(parsed.ast_root):
        callee = get_call_name(call)
        if callee is None or callee.split(".")[-1] not in _SQL_EXEC_METHODS:
            continue
        if call.args and is_dynamic_string(call.args[0]):
            results.append(match_from_node(parsed, call))
    return results


def _has_shell_true(call: ast.Call) -> bool:
    return any(
        kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True
        for kw in call.keywords
    )


@register_matcher("CMD001")
def match_command_injection(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for call in find_calls(parsed.ast_root):
        callee = get_call_name(call)
        if callee not in _SHELL_EXEC_FUNCS:
            continue
        if not call.args:
            continue
        dynamic_arg = is_dynamic_string(call.args[0])
        if callee == "os.system" or callee == "os.popen":
            if dynamic_arg:
                results.append(match_from_node(parsed, call))
        elif _has_shell_true(call) and dynamic_arg:
            results.append(match_from_node(parsed, call))
    return results


@register_matcher("CODE001")
def match_unsafe_eval(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for call in find_calls(parsed.ast_root):
        callee = get_call_name(call)
        if callee not in _EVAL_FUNCS:
            continue
        if call.args and is_dynamic_string(call.args[0]):
            results.append(match_from_node(parsed, call))
    return results
