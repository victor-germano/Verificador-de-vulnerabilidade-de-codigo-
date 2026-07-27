"""Shared helpers for writing Python AST-based matchers.

Every matcher in this package follows the same shape: walk `parsed.ast_root`
(an `ast.Module`), find `ast.Call` nodes whose callee matches a known
dangerous name, and flag them when at least one relevant argument is *not*
a compile-time constant (i.e. it was built dynamically from a variable,
f-string, concatenation or `.format()` call - the pattern that makes
injection possible).
"""

from __future__ import annotations

import ast

from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult


def get_call_name(node: ast.Call) -> str | None:
    """Returns the dotted callee name, e.g. `os.system`, `eval`, `cursor.execute`."""
    func = node.func
    parts: list[str] = []
    while isinstance(func, ast.Attribute):
        parts.append(func.attr)
        func = func.value
    if isinstance(func, ast.Name):
        parts.append(func.id)
        return ".".join(reversed(parts))
    return None


def is_dynamic_string(node: ast.expr | None) -> bool:
    """True if `node` builds a string at runtime rather than being a literal."""
    if node is None:
        return False
    if isinstance(node, ast.Constant):
        return False
    if isinstance(node, ast.JoinedStr):  # f-string
        return True
    if isinstance(node, ast.BinOp):  # "a" + b, "a %s" % b
        return True
    return isinstance(node, ast.Call | ast.Name)


def find_calls(tree: ast.AST) -> list[ast.Call]:
    return [n for n in ast.walk(tree) if isinstance(n, ast.Call)]


def match_from_node(parsed: ParsedFile, node: ast.AST, note: str | None = None) -> MatchResult:
    line_start = getattr(node, "lineno", 1)
    line_end = getattr(node, "end_lineno", line_start)
    return MatchResult(
        line_start=line_start,
        line_end=line_end,
        snippet=parsed.snippet(line_start, line_end),
        note=note,
    )
