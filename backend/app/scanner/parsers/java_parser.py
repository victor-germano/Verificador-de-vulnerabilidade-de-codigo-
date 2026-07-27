from pathlib import Path

import tree_sitter_java as tsjava
from tree_sitter import Language as TSLanguage
from tree_sitter import Parser

from app.models.enums import Language
from app.scanner.parsers.base import ParsedFile

_JAVA_LANGUAGE = TSLanguage(tsjava.language())


class JavaParser:
    """Parses Java using tree-sitter - the first AST-backed adapter for a
    language beyond Python/JS/TS, added to demonstrate the extension point
    described in `docs/adding-a-language.md`."""

    language = Language.JAVA
    extensions = {".java"}

    def __init__(self) -> None:
        self._parser = Parser(_JAVA_LANGUAGE)

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
