"""Parser contracts.

Every language adapter turns raw source text into a `ParsedFile`. `ast_root`
is intentionally typed as `Any`: a Python `ast.Module`, a `tree_sitter.Tree`,
or `None` (languages without a dedicated AST adapter yet - see
`generic_regex_parser`). Rule matchers know how to read whichever shape their
own language produces; the engine never inspects `ast_root` itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from app.models.enums import Language


@dataclass(frozen=True)
class ParsedFile:
    path: Path
    language: Language
    source: str
    lines: list[str] = field(default_factory=list)
    ast_root: Any | None = None
    parse_error: str | None = None

    def snippet(self, line_start: int, line_end: int | None = None) -> str:
        end = line_end or line_start
        start_idx = max(0, line_start - 1)
        end_idx = min(len(self.lines), end)
        return "\n".join(self.lines[start_idx:end_idx])


class LanguageParser(Protocol):
    """Contract every language-specific parser adapter must satisfy."""

    language: Language
    extensions: set[str]

    def can_parse(self, path: Path) -> bool: ...

    def parse(self, path: Path, source: str) -> ParsedFile: ...
