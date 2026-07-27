from tree_sitter import Node

from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult, register_matcher
from app.scanner.rules.matchers._ts_utils import match_from_ts_node, node_text, walk


def _unwrap_argument(wrapper: Node) -> Node:
    """C# wraps each call argument in an `argument` node (to support named
    arguments/`ref`/`out` modifiers); unwrap it to get the actual expression."""
    return wrapper.children[0] if wrapper.children else wrapper


@register_matcher("CSHARPSQL001")
def match_sql_injection(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    source = parsed.source.encode("utf-8")
    results: list[MatchResult] = []
    for node in walk(parsed.ast_root.root_node):
        if node.type != "object_creation_expression":
            continue
        type_node = node.child_by_field_name("type")
        if type_node is None or node_text(source, type_node) != "SqlCommand":
            continue
        args_node = node.child_by_field_name("arguments")
        if args_node is None:
            continue
        wrapper = next(iter(args_node.named_children), None)
        if wrapper is not None and _unwrap_argument(wrapper).type == "binary_expression":
            results.append(match_from_ts_node(parsed, node))
    return results


@register_matcher("CSHARPCMD001")
def match_command_injection(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    source = parsed.source.encode("utf-8")
    results: list[MatchResult] = []
    for node in walk(parsed.ast_root.root_node):
        if node.type != "invocation_expression":
            continue
        func_node = node.child_by_field_name("function")
        if func_node is None or func_node.type != "member_access_expression":
            continue
        expr_node = func_node.child_by_field_name("expression")
        name_node = func_node.child_by_field_name("name")
        if expr_node is None or name_node is None:
            continue
        if node_text(source, expr_node) != "Process" or node_text(source, name_node) != "Start":
            continue
        args_node = node.child_by_field_name("arguments")
        if args_node is None:
            continue
        if any(
            _unwrap_argument(wrapper).type != "string_literal"
            for wrapper in args_node.named_children
        ):
            results.append(match_from_ts_node(parsed, node))
    return results
