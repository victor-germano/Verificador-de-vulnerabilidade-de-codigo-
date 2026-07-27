from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult, register_matcher
from app.scanner.rules.matchers._ts_utils import match_from_ts_node, node_text, walk

_SQL_METHODS = {"Query", "Exec", "QueryRow", "QueryContext", "ExecContext", "QueryRowContext"}
_STRING_LITERAL_TYPES = {"interpreted_string_literal", "raw_string_literal"}


@register_matcher("GOSQL001")
def match_sql_injection(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    source = parsed.source.encode("utf-8")
    results: list[MatchResult] = []
    for node in walk(parsed.ast_root.root_node):
        if node.type != "call_expression":
            continue
        func_node = node.child_by_field_name("function")
        if func_node is None or func_node.type != "selector_expression":
            continue
        field_node = func_node.child_by_field_name("field")
        if field_node is None or node_text(source, field_node) not in _SQL_METHODS:
            continue
        args_node = node.child_by_field_name("arguments")
        if args_node is None:
            continue
        first_arg = next(iter(args_node.named_children), None)
        if first_arg is not None and first_arg.type == "binary_expression":
            results.append(match_from_ts_node(parsed, node))
    return results


@register_matcher("GOCMD001")
def match_command_injection(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    source = parsed.source.encode("utf-8")
    results: list[MatchResult] = []
    for node in walk(parsed.ast_root.root_node):
        if node.type != "call_expression":
            continue
        func_node = node.child_by_field_name("function")
        if func_node is None or func_node.type != "selector_expression":
            continue
        field_node = func_node.child_by_field_name("field")
        if field_node is None or node_text(source, field_node) != "Command":
            continue
        args_node = node.child_by_field_name("arguments")
        if args_node is None:
            continue
        if any(arg.type not in _STRING_LITERAL_TYPES for arg in args_node.named_children):
            results.append(match_from_ts_node(parsed, node))
    return results
