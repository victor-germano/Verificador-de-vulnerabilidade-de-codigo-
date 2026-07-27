from pathlib import Path

import tree_sitter_c_sharp as tscsharp
from tree_sitter import Language as TSLanguage
from tree_sitter import Parser

from app.models.enums import Language
from app.scanner.parsers.base import ParsedFile

_CSHARP_LANGUAGE = TSLanguage(tscsharp.language())


class CSharpParser:
    """Parses C# using tree-sitter."""

    language = Language.CSHARP
    extensions = {".cs"}

    def __init__(self) -> None:
        self._parser = Parser(_CSHARP_LANGUAGE)

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
