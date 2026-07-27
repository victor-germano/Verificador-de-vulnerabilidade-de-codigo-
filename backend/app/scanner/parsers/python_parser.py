import ast
from pathlib import Path

from app.models.enums import Language
from app.scanner.parsers.base import ParsedFile


class PythonParser:
    """Parses Python source into its native `ast.Module` - no third-party
    dependency needed, and it is the most precise AST available to us."""

    language = Language.PYTHON
    extensions = {".py"}

    def can_parse(self, path: Path) -> bool:
        return path.suffix in self.extensions

    def parse(self, path: Path, source: str) -> ParsedFile:
        try:
            tree = ast.parse(source, filename=str(path))
            return ParsedFile(
                path=path,
                language=self.language,
                source=source,
                lines=source.splitlines(),
                ast_root=tree,
            )
        except SyntaxError as exc:
            return ParsedFile(
                path=path,
                language=self.language,
                source=source,
                lines=source.splitlines(),
                ast_root=None,
                parse_error=str(exc),
            )
