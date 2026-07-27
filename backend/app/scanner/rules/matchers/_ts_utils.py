"""Shared helpers for every tree-sitter based matcher (JS, TS, Java, ...).

`parsed.ast_root` for tree-sitter-backed languages is a `tree_sitter.Tree`
(see e.g. `javascript_parser.py`, `java_parser.py`); these helpers walk it
and translate byte offsets back into the 1-based line numbers the rest of
the engine works with.
"""

from __future__ import annotations

from collections.abc import Iterator

from tree_sitter import Node

from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult


def walk(node: Node) -> Iterator[Node]:
    yield node
    for child in node.children:
        yield from walk(child)


def node_text(source: bytes, node: Node) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def match_from_ts_node(parsed: ParsedFile, node: Node, note: str | None = None) -> MatchResult:
    line_start = node.start_point[0] + 1
    line_end = node.end_point[0] + 1
    return MatchResult(
        line_start=line_start,
        line_end=line_end,
        snippet=parsed.snippet(line_start, line_end),
        note=note,
    )
