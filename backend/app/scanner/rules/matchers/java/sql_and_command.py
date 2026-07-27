from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult, register_matcher
from app.scanner.rules.matchers._ts_utils import match_from_ts_node, node_text, walk

_SQL_EXEC_METHODS = {"executeQuery", "executeUpdate", "execute"}


@register_matcher("JAVASQL001")
def match_sql_injection(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    source = parsed.source.encode("utf-8")
    results: list[MatchResult] = []
    for node in walk(parsed.ast_root.root_node):
        if node.type != "method_invocation":
            continue
        name_node = node.child_by_field_name("name")
        if name_node is None or node_text(source, name_node) not in _SQL_EXEC_METHODS:
            continue
        args_node = node.child_by_field_name("arguments")
        if args_node is None:
            continue
        first_arg = next(iter(args_node.named_children), None)
        if first_arg is not None and first_arg.type == "binary_expression":
            results.append(match_from_ts_node(parsed, node))
    return results


@register_matcher("JAVACMD001")
def match_command_injection(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    source = parsed.source.encode("utf-8")
    results: list[MatchResult] = []
    for node in walk(parsed.ast_root.root_node):
        if node.type != "method_invocation":
            continue
        name_node = node.child_by_field_name("name")
        if name_node is None or node_text(source, name_node) != "exec":
            continue
        args_node = node.child_by_field_name("arguments")
        if args_node is None:
            continue
        first_arg = next(iter(args_node.named_children), None)
        if first_arg is not None and first_arg.type != "string_literal":
            results.append(match_from_ts_node(parsed, node))
    return results
