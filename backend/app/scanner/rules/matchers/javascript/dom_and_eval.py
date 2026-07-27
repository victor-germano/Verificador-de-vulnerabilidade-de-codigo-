from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult, register_matcher
from app.scanner.rules.matchers._ts_utils import match_from_ts_node, node_text, walk

_TIMER_FUNCS = {"setTimeout", "setInterval"}


@register_matcher("JSEVAL001")
def match_unsafe_eval(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    source = parsed.source.encode("utf-8")
    results: list[MatchResult] = []
    for node in walk(parsed.ast_root.root_node):
        if node.type == "call_expression":
            func_node = node.child_by_field_name("function")
            if func_node is None:
                continue
            func_text = node_text(source, func_node)
            if func_text == "eval":
                results.append(match_from_ts_node(parsed, node))
                continue
            if func_text in _TIMER_FUNCS:
                args_node = node.child_by_field_name("arguments")
                if args_node is None:
                    continue
                first_arg = next((c for c in args_node.named_children), None)
                if first_arg is not None and first_arg.type == "string":
                    results.append(match_from_ts_node(parsed, node))
        elif node.type == "new_expression":
            ctor_node = node.child_by_field_name("constructor")
            if ctor_node is not None and node_text(source, ctor_node) == "Function":
                results.append(match_from_ts_node(parsed, node))
    return results


@register_matcher("JSXSS001")
def match_dom_xss(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    source = parsed.source.encode("utf-8")
    results: list[MatchResult] = []
    for node in walk(parsed.ast_root.root_node):
        if node.type == "assignment_expression":
            left = node.child_by_field_name("left")
            right = node.child_by_field_name("right")
            if left is None or right is None or left.type != "member_expression":
                continue
            prop_node = left.child_by_field_name("property")
            if prop_node is None:
                continue
            prop_name = node_text(source, prop_node)
            if prop_name in {"innerHTML", "outerHTML"} and right.type != "string":
                results.append(match_from_ts_node(parsed, node))
        elif node.type == "call_expression":
            func_node = node.child_by_field_name("function")
            if func_node is not None and node_text(source, func_node) == "document.write":
                results.append(match_from_ts_node(parsed, node))
    return results
