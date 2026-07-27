import ast

from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult, register_matcher
from app.scanner.rules.matchers.python._ast_utils import (
    find_calls,
    get_call_name,
    is_dynamic_string,
    match_from_node,
)


@register_matcher("XSS001")
def match_reflected_xss(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for call in find_calls(parsed.ast_root):
        if get_call_name(call) != "render_template_string":
            continue
        if call.args and is_dynamic_string(call.args[0]):
            results.append(match_from_node(parsed, call))
    return results


def _bool_kwarg_is_true(call: ast.Call, name: str) -> bool:
    for kw in call.keywords:
        if kw.arg == name and isinstance(kw.value, ast.Constant) and kw.value.value is True:
            return True
    return False


@register_matcher("COOKIE001")
def match_insecure_cookie(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for call in find_calls(parsed.ast_root):
        callee = get_call_name(call)
        if callee is None or callee.split(".")[-1] != "set_cookie":
            continue
        if not (_bool_kwarg_is_true(call, "secure") and _bool_kwarg_is_true(call, "httponly")):
            results.append(match_from_node(parsed, call))
    return results


@register_matcher("REDIRECT001")
def match_open_redirect(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for call in find_calls(parsed.ast_root):
        if get_call_name(call) != "redirect" or not call.args:
            continue
        arg = call.args[0]
        # Flags request.args.get(...)/request.values.get(...) fed straight
        # into redirect() without going through a validation helper first.
        if isinstance(arg, ast.Call):
            arg_callee = get_call_name(arg) or ""
            if arg_callee.startswith("request."):
                results.append(match_from_node(parsed, call))
    return results
