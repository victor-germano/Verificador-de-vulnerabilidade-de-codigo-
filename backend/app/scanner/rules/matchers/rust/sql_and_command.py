from tree_sitter import Node

from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult, register_matcher
from app.scanner.rules.matchers._ts_utils import match_from_ts_node, node_text, walk

_SQL_METHODS = {"execute", "query"}


def _contains_format_macro(node: Node, source: bytes) -> bool:
    for n in walk(node):
        if n.type != "macro_invocation":
            continue
        macro_node = n.child_by_field_name("macro")
        if macro_node is not None and node_text(source, macro_node) == "format":
            return True
    return False


@register_matcher("RUSTSQL001")
def match_sql_injection(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    source = parsed.source.encode("utf-8")
    results: list[MatchResult] = []
    for node in walk(parsed.ast_root.root_node):
        if node.type != "call_expression":
            continue
        func_node = node.child_by_field_name("function")
        if func_node is None or func_node.type != "field_expression":
            continue
        field_node = func_node.child_by_field_name("field")
        if field_node is None or node_text(source, field_node) not in _SQL_METHODS:
            continue
        args_node = node.child_by_field_name("arguments")
        if args_node is None:
            continue
        first_arg = next(iter(args_node.named_children), None)
        if first_arg is not None and _contains_format_macro(first_arg, source):
            results.append(match_from_ts_node(parsed, node))
    return results


@register_matcher("RUSTCMD001")
def match_command_injection(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    source = parsed.source.encode("utf-8")
    results: list[MatchResult] = []
    for node in walk(parsed.ast_root.root_node):
        if node.type != "call_expression":
            continue
        func_node = node.child_by_field_name("function")
        if func_node is None or func_node.type != "scoped_identifier":
            continue
        path_node = func_node.child_by_field_name("path")
        name_node = func_node.child_by_field_name("name")
        if path_node is None or name_node is None:
            continue
        if node_text(source, path_node) != "Command" or node_text(source, name_node) != "new":
            continue
        args_node = node.child_by_field_name("arguments")
        if args_node is None:
            continue
        first_arg = next(iter(args_node.named_children), None)
        if first_arg is not None and first_arg.type != "string_literal":
            results.append(match_from_ts_node(parsed, node))
    return results
