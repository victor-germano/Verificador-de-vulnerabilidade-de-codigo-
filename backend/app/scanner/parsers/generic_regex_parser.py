"""Fallback parser for languages without a dedicated AST adapter yet.

`ast_root` stays `None` - only regex-based rules (registered under
`app.scanner.rules.matchers.generic`) run against files handled by this
parser. This is the extension point described in
`docs/adding-a-language.md`: adding a real AST parser only requires
implementing `LanguageParser` and registering it in `ParserRegistry`,
nothing in the engine changes.

Every language in the initial catalog (Python, JS, TS, Java, PHP, Go, Rust,
C#) now has a dedicated AST parser, so `EXTENSION_TO_LANGUAGE` is empty -
this class stays as the landing spot for the *next* language added without
AST support yet.
"""

from pathlib import Path

from app.models.enums import Language
from app.scanner.parsers.base import ParsedFile

EXTENSION_TO_LANGUAGE: dict[str, Language] = {}


class GenericRegexParser:
    """One instance covers every extension in `EXTENSION_TO_LANGUAGE`."""

    extensions = set(EXTENSION_TO_LANGUAGE)

    def can_parse(self, path: Path) -> bool:
        return path.suffix in self.extensions

    def language_for(self, path: Path) -> Language:
        return EXTENSION_TO_LANGUAGE[path.suffix]

    def parse(self, path: Path, source: str) -> ParsedFile:
        return ParsedFile(
            path=path,
            language=self.language_for(path),
            source=source,
            lines=source.splitlines(),
            ast_root=None,
        )
