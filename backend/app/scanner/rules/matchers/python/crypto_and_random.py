import ast

from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult, register_matcher
from app.scanner.rules.matchers.python._ast_utils import find_calls, get_call_name, match_from_node

_WEAK_HASH_FUNCS = {"hashlib.md5", "hashlib.sha1"}
_RANDOM_FUNCS = {
    "random.random",
    "random.randint",
    "random.randrange",
    "random.choice",
    "random.getrandbits",
}
_SENSITIVE_NAME_HINTS = ("password", "senha", "token", "secret", "key", "otp", "pin")


@register_matcher("CRYPTO001")
def match_weak_hash(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for call in find_calls(parsed.ast_root):
        if get_call_name(call) in _WEAK_HASH_FUNCS:
            results.append(match_from_node(parsed, call))
    return results


def _target_name_is_sensitive(node: ast.Assign) -> bool:
    for target in node.targets:
        name = getattr(target, "id", "") or ""
        if any(hint in name.lower() for hint in _SENSITIVE_NAME_HINTS):
            return True
    return False


@register_matcher("RANDOM001")
def match_weak_random(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for node in ast.walk(parsed.ast_root):
        if not isinstance(node, ast.Assign) or not _target_name_is_sensitive(node):
            continue
        for call in ast.walk(node.value):
            if isinstance(call, ast.Call) and get_call_name(call) in _RANDOM_FUNCS:
                results.append(match_from_node(parsed, node))
                break
    return results
