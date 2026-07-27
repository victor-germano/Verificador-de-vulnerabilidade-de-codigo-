from pathlib import Path

import tree_sitter_php as tsphp
from tree_sitter import Language as TSLanguage
from tree_sitter import Parser

from app.models.enums import Language
from app.scanner.parsers.base import ParsedFile

_PHP_LANGUAGE = TSLanguage(tsphp.language_php())


class PhpParser:
    """Parses PHP using tree-sitter. `language_php` (not `language_php_only`)
    is used since real `.php` files commonly mix HTML with PHP tags."""

    language = Language.PHP
    extensions = {".php"}

    def __init__(self) -> None:
        self._parser = Parser(_PHP_LANGUAGE)

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
