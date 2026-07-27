from pathlib import Path

import tree_sitter_typescript as tstypescript
from tree_sitter import Language as TSLanguage
from tree_sitter import Parser

from app.models.enums import Language
from app.scanner.parsers.base import ParsedFile

_TS_LANGUAGE = TSLanguage(tstypescript.language_typescript())
_TSX_LANGUAGE = TSLanguage(tstypescript.language_tsx())


class TypeScriptParser:
    """Parses TS/TSX using tree-sitter. `.tsx` uses the TSX grammar variant
    (which also understands embedded JSX), `.ts` uses the plain grammar."""

    language = Language.TYPESCRIPT
    extensions = {".ts", ".tsx"}

    def __init__(self) -> None:
        self._ts_parser = Parser(_TS_LANGUAGE)
        self._tsx_parser = Parser(_TSX_LANGUAGE)

    def can_parse(self, path: Path) -> bool:
        return path.suffix in self.extensions

    def parse(self, path: Path, source: str) -> ParsedFile:
        parser = self._tsx_parser if path.suffix == ".tsx" else self._ts_parser
        tree = parser.parse(bytes(source, "utf-8"))
        return ParsedFile(
            path=path,
            language=self.language,
            source=source,
            lines=source.splitlines(),
            ast_root=tree,
        )
