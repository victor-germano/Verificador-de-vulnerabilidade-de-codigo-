from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult, register_matcher
from app.scanner.rules.matchers._ts_utils import match_from_ts_node, node_text, walk

_EXEC_FUNCS = {"exec", "execSync"}


@register_matcher("JSCMD001")
def match_command_injection(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    source = parsed.source.encode("utf-8")
    results: list[MatchResult] = []
    for node in walk(parsed.ast_root.root_node):
        if node.type != "call_expression":
            continue
        func_node = node.child_by_field_name("function")
        if func_node is None:
            continue
        callee = node_text(source, func_node).split(".")[-1]
        if callee not in _EXEC_FUNCS:
            continue
        args_node = node.child_by_field_name("arguments")
        if args_node is None:
            continue
        first_arg = next(iter(args_node.named_children), None)
        if first_arg is not None and first_arg.type != "string":
            results.append(match_from_ts_node(parsed, node))
    return results
