import ast

from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult, register_matcher
from app.scanner.rules.matchers.python._ast_utils import (
    find_calls,
    get_call_name,
    is_dynamic_string,
    match_from_node,
)

_DYNAMIC_IMPORT_FUNCS = {"importlib.import_module", "__import__"}


def _is_concatenated(node: ast.expr) -> bool:
    """Narrower than `is_dynamic_string`: only f-strings/`+` concatenation,
    not a bare variable - used where a bare `Name` alone would be too noisy
    a signal (e.g. LDAP/XPath queries commonly pass a pre-built filter)."""
    return isinstance(node, ast.JoinedStr | ast.BinOp)


@register_matcher("NOSQL001")
def match_nosql_injection(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for node in ast.walk(parsed.ast_root):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values, strict=False):
            if (
                isinstance(key, ast.Constant)
                and key.value == "$where"
                and value is not None
                and is_dynamic_string(value)
            ):
                results.append(match_from_node(parsed, node))
    return results


@register_matcher("SSTI001")
def match_ssti(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for call in find_calls(parsed.ast_root):
        callee = get_call_name(call)
        if callee is None or not call.args:
            continue
        is_template_ctor = callee in {"Template", "jinja2.Template"}
        is_from_string = callee.split(".")[-1] == "from_string"
        if (is_template_ctor or is_from_string) and is_dynamic_string(call.args[0]):
            results.append(match_from_node(parsed, call))
    return results


@register_matcher("LDAP001")
def match_ldap_injection(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for call in find_calls(parsed.ast_root):
        callee = get_call_name(call)
        if callee is None or callee.split(".")[-1] not in {"search", "search_s"}:
            continue
        if any(_is_concatenated(arg) for arg in call.args):
            results.append(match_from_node(parsed, call))
    return results


@register_matcher("XPATH001")
def match_xpath_injection(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for call in find_calls(parsed.ast_root):
        callee = get_call_name(call)
        if callee is None or callee.split(".")[-1] != "xpath":
            continue
        if call.args and _is_concatenated(call.args[0]):
            results.append(match_from_node(parsed, call))
    return results


@register_matcher("UPLOAD001")
def match_unsafe_file_upload(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for call in find_calls(parsed.ast_root):
        callee = get_call_name(call)
        if callee is None or callee.split(".")[-1] != "save":
            continue
        for arg in [*call.args, *(kw.value for kw in call.keywords)]:
            has_raw_filename = any(
                isinstance(n, ast.Attribute) and n.attr == "filename" for n in ast.walk(arg)
            )
            is_sanitized = any(
                isinstance(n, ast.Call)
                and (get_call_name(n) or "").split(".")[-1] == "secure_filename"
                for n in ast.walk(arg)
            )
            if has_raw_filename and not is_sanitized:
                results.append(match_from_node(parsed, call))
                break
    return results


@register_matcher("REFLECT001")
def match_unsafe_reflection(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for call in find_calls(parsed.ast_root):
        inner = call.func
        if not isinstance(inner, ast.Call) or get_call_name(inner) != "getattr":
            continue
        if len(inner.args) != 2:
            continue
        if not isinstance(inner.args[1], ast.Constant):
            results.append(match_from_node(parsed, call))
    return results


@register_matcher("FILEINC001")
def match_unsafe_dynamic_import(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for call in find_calls(parsed.ast_root):
        callee = get_call_name(call)
        if callee not in _DYNAMIC_IMPORT_FUNCS or not call.args:
            continue
        if not isinstance(call.args[0], ast.Constant):
            results.append(match_from_node(parsed, call))
    return results


@register_matcher("TEMPFILE001")
def match_insecure_tempfile(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for call in find_calls(parsed.ast_root):
        if get_call_name(call) == "tempfile.mktemp":
            results.append(match_from_node(parsed, call))
    return results
