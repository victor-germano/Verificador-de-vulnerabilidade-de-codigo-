import ast

from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult, register_matcher
from app.scanner.rules.matchers.python._ast_utils import find_calls, get_call_name, match_from_node

_UNSAFE_DESERIALIZE_FUNCS = {"pickle.load", "pickle.loads", "marshal.load", "marshal.loads"}
_XML_PARSE_FUNCS = {
    "xml.etree.ElementTree.parse",
    "xml.etree.ElementTree.fromstring",
    "ElementTree.parse",
    "ElementTree.fromstring",
    "xml.sax.parse",
    "xml.dom.minidom.parse",
    "xml.dom.minidom.parseString",
}


def _is_yaml_load_without_safe_loader(call: ast.Call) -> bool:
    if get_call_name(call) != "yaml.load":
        return False
    for kw in call.keywords:
        if kw.arg == "Loader":
            loader_name = getattr(kw.value, "attr", None) or getattr(kw.value, "id", None)
            if loader_name == "SafeLoader":
                return False
    return True


@register_matcher("DESER001")
def match_insecure_deserialization(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for call in find_calls(parsed.ast_root):
        callee = get_call_name(call)
        if callee in _UNSAFE_DESERIALIZE_FUNCS or _is_yaml_load_without_safe_loader(call):
            results.append(match_from_node(parsed, call))
    return results


@register_matcher("XXE001")
def match_xxe(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for call in find_calls(parsed.ast_root):
        callee = get_call_name(call)
        if callee in _XML_PARSE_FUNCS:
            results.append(match_from_node(parsed, call))
    return results
