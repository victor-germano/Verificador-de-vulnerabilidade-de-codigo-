import ast

from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult, register_matcher
from app.scanner.rules.matchers.python._ast_utils import find_calls, get_call_name, match_from_node


@register_matcher("RESOURCE001")
def match_resource_leak(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []

    protected_ids: set[int] = set()
    for node in ast.walk(parsed.ast_root):
        if not isinstance(node, ast.With | ast.AsyncWith):
            continue
        for item in node.items:
            for call in ast.walk(item.context_expr):
                if isinstance(call, ast.Call) and get_call_name(call) == "open":
                    protected_ids.add(id(call))

    results: list[MatchResult] = []
    for call in find_calls(parsed.ast_root):
        if get_call_name(call) == "open" and id(call) not in protected_ids:
            results.append(match_from_node(parsed, call))
    return results
