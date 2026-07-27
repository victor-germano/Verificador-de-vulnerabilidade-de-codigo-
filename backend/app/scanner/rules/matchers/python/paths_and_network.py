from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult, register_matcher
from app.scanner.rules.matchers.python._ast_utils import find_calls, get_call_name, match_from_node

_FILE_OPEN_FUNCS = {"open", "os.remove", "os.unlink", "os.rmdir", "shutil.rmtree"}
_HTTP_GET_FUNCS = {
    "requests.get",
    "requests.post",
    "requests.put",
    "requests.delete",
    "requests.request",
    "httpx.get",
    "httpx.post",
    "urllib.request.urlopen",
}
_PATH_HINT_NAMES = {"path", "filepath", "filename", "file_path", "file_name"}


@register_matcher("PATH001")
def match_path_traversal(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for call in find_calls(parsed.ast_root):
        callee = get_call_name(call)
        if callee not in _FILE_OPEN_FUNCS or not call.args:
            continue
        arg = call.args[0]
        # Heuristic: os.path.join(...) or an f-string/BinOp/Name feeding the
        # file operation, i.e. anything that is not a literal constant path.
        is_join_call = hasattr(arg, "func") and get_call_name(arg) == "os.path.join"
        is_dynamic = type(arg).__name__ in {"Name", "JoinedStr", "BinOp"} or is_join_call
        if is_dynamic:
            results.append(match_from_node(parsed, call))
    return results


@register_matcher("SSRF001")
def match_ssrf(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    results: list[MatchResult] = []
    for call in find_calls(parsed.ast_root):
        callee = get_call_name(call)
        if callee not in _HTTP_GET_FUNCS or not call.args:
            continue
        arg = call.args[0]
        if type(arg).__name__ in {"Name", "JoinedStr", "BinOp"}:
            results.append(match_from_node(parsed, call))
    return results
