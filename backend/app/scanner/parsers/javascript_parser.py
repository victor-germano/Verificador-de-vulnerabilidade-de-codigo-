from pathlib import Path

import tree_sitter_javascript as tsjavascript
from tree_sitter import Language as TSLanguage
from tree_sitter import Parser

from app.models.enums import Language
from app.scanner.parsers.base import ParsedFile

_JS_LANGUAGE = TSLanguage(tsjavascript.language())


class JavaScriptParser:
    """Parses JS/JSX using tree-sitter, giving matchers a real syntax tree
    instead of relying purely on regex heuristics."""

    language = Language.JAVASCRIPT
    extensions = {".js", ".jsx"}

    def __init__(self) -> None:
        self._parser = Parser(_JS_LANGUAGE)

    def can_parse(self, path: Path) -> bool:
        return path.suffix in self.extensions

    def parse(self, path: Path, source: str) -> ParsedFile:
        tree = self._parser.parse(bytes(source, "utf-8"))
        return ParsedFile(
            path=path,
            language=self.language,
            source=source,
            lines=source.splitlines(),
            ast_root=tree,
        )
