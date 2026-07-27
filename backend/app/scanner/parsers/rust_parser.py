from pathlib import Path

import tree_sitter_rust as tsrust
from tree_sitter import Language as TSLanguage
from tree_sitter import Parser

from app.models.enums import Language
from app.scanner.parsers.base import ParsedFile

_RUST_LANGUAGE = TSLanguage(tsrust.language())


class RustParser:
    """Parses Rust using tree-sitter."""

    language = Language.RUST
    extensions = {".rs"}

    def __init__(self) -> None:
        self._parser = Parser(_RUST_LANGUAGE)

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
