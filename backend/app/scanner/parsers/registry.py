from pathlib import Path

from app.scanner.parsers.base import ParsedFile
from app.scanner.parsers.csharp_parser import CSharpParser
from app.scanner.parsers.generic_regex_parser import GenericRegexParser
from app.scanner.parsers.go_parser import GoParser
from app.scanner.parsers.java_parser import JavaParser
from app.scanner.parsers.javascript_parser import JavaScriptParser
from app.scanner.parsers.php_parser import PhpParser
from app.scanner.parsers.python_parser import PythonParser
from app.scanner.parsers.rust_parser import RustParser
from app.scanner.parsers.typescript_parser import TypeScriptParser


class ParserRegistry:
    """Resolves the right `LanguageParser` for a file by extension.

    To add a new language: implement a parser adapter (see
    `docs/adding-a-language.md`) and append it to `_dedicated_parsers`. No
    other part of the scanner engine needs to change.
    """

    def __init__(self) -> None:
        self._dedicated_parsers = [
            PythonParser(),
            JavaScriptParser(),
            TypeScriptParser(),
            JavaParser(),
            PhpParser(),
            GoParser(),
            RustParser(),
            CSharpParser(),
        ]
        self._fallback_parser = GenericRegexParser()

    @property
    def supported_extensions(self) -> set[str]:
        extensions = {ext for p in self._dedicated_parsers for ext in p.extensions}
        return extensions | self._fallback_parser.extensions

    def get_parser_for(self, path: Path):
        for parser in self._dedicated_parsers:
            if parser.can_parse(path):
                return parser
        if self._fallback_parser.can_parse(path):
            return self._fallback_parser
        return None

    def parse(self, path: Path, source: str) -> ParsedFile | None:
        parser = self.get_parser_for(path)
        if parser is None:
            return None
        return parser.parse(path, source)
