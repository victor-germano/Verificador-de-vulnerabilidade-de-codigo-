from tree_sitter import Node

from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult, register_matcher
from app.scanner.rules.matchers._ts_utils import match_from_ts_node, node_text, walk

_SQL_FUNCTIONS = {"mysqli_query", "mysql_query", "pg_query"}
_SQL_METHODS = {"query", "exec"}
_CMD_FUNCTIONS = {"exec", "shell_exec", "system", "passthru", "popen", "proc_open"}
_STRING_LITERAL_TYPES = {"string", "encapsed_string"}


def _unwrap_argument(wrapper: Node) -> Node:
    """PHP wraps each call argument in an `argument` node (to support named
    arguments, `foo(name: $value)`); unwrap it to get the actual expression."""
    return wrapper.children[0] if wrapper.children else wrapper


def _nth_argument_expr(node: Node, index: int) -> Node | None:
    args_node = node.child_by_field_name("arguments")
    if args_node is None:
        return None
    wrappers = list(args_node.named_children)
    if index >= len(wrappers) or index < -len(wrappers):
        return None
    return _unwrap_argument(wrappers[index])


@register_matcher("PHPSQL001")
def match_sql_injection(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    source = parsed.source.encode("utf-8")
    results: list[MatchResult] = []
    for node in walk(parsed.ast_root.root_node):
        if node.type == "function_call_expression":
            func_node = node.child_by_field_name("function")
            if func_node is None or node_text(source, func_node) not in _SQL_FUNCTIONS:
                continue
            expr = _nth_argument_expr(node, -1)
        elif node.type == "member_call_expression":
            name_node = node.child_by_field_name("name")
            if name_node is None or node_text(source, name_node) not in _SQL_METHODS:
                continue
            expr = _nth_argument_expr(node, 0)
        else:
            continue

        if expr is not None and expr.type == "binary_expression":
            results.append(match_from_ts_node(parsed, node))
    return results


@register_matcher("PHPCMD001")
def match_command_injection(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    source = parsed.source.encode("utf-8")
    results: list[MatchResult] = []
    for node in walk(parsed.ast_root.root_node):
        if node.type != "function_call_expression":
            continue
        func_node = node.child_by_field_name("function")
        if func_node is None or node_text(source, func_node) not in _CMD_FUNCTIONS:
            continue
        expr = _nth_argument_expr(node, 0)
        if expr is not None and expr.type not in _STRING_LITERAL_TYPES:
            results.append(match_from_ts_node(parsed, node))
    return results
