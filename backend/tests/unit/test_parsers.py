from pathlib import Path

from app.models.enums import Language
from app.scanner.parsers.csharp_parser import CSharpParser
from app.scanner.parsers.generic_regex_parser import EXTENSION_TO_LANGUAGE, GenericRegexParser
from app.scanner.parsers.go_parser import GoParser
from app.scanner.parsers.java_parser import JavaParser
from app.scanner.parsers.javascript_parser import JavaScriptParser
from app.scanner.parsers.php_parser import PhpParser
from app.scanner.parsers.python_parser import PythonParser
from app.scanner.parsers.registry import ParserRegistry
from app.scanner.parsers.rust_parser import RustParser
from app.scanner.parsers.typescript_parser import TypeScriptParser


def test_python_parser_parses_valid_source() -> None:
    parser = PythonParser()
    parsed = parser.parse(Path("sample.py"), "x = 1\n")
    assert parsed.language == Language.PYTHON
    assert parsed.ast_root is not None
    assert parsed.parse_error is None


def test_python_parser_reports_syntax_error() -> None:
    parser = PythonParser()
    parsed = parser.parse(Path("broken.py"), "def foo(:\n")
    assert parsed.ast_root is None
    assert parsed.parse_error is not None


def test_python_parser_can_parse_extension() -> None:
    parser = PythonParser()
    assert parser.can_parse(Path("a.py"))
    assert not parser.can_parse(Path("a.js"))


def test_javascript_parser_builds_tree() -> None:
    parser = JavaScriptParser()
    parsed = parser.parse(Path("sample.js"), "const x = 1;")
    assert parsed.language == Language.JAVASCRIPT
    assert parsed.ast_root is not None
    assert parsed.ast_root.root_node.type == "program"


def test_typescript_parser_builds_tree_for_ts_and_tsx() -> None:
    parser = TypeScriptParser()
    ts_parsed = parser.parse(Path("sample.ts"), "const x: number = 1;")
    tsx_parsed = parser.parse(Path("sample.tsx"), "const el = <div />;")
    assert ts_parsed.language == Language.TYPESCRIPT
    assert ts_parsed.ast_root is not None
    assert tsx_parsed.ast_root is not None


def test_java_parser_builds_tree() -> None:
    parser = JavaParser()
    parsed = parser.parse(Path("Main.java"), "class Main {}")
    assert parsed.language == Language.JAVA
    assert parsed.ast_root is not None
    assert parsed.ast_root.root_node.type == "program"


def test_php_parser_builds_tree() -> None:
    parser = PhpParser()
    parsed = parser.parse(Path("index.php"), "<?php echo 1; ?>")
    assert parsed.language == Language.PHP
    assert parsed.ast_root is not None


def test_go_parser_builds_tree() -> None:
    parser = GoParser()
    parsed = parser.parse(Path("main.go"), "package main\nfunc main() {}\n")
    assert parsed.language == Language.GO
    assert parsed.ast_root is not None
    assert parsed.ast_root.root_node.type == "source_file"


def test_rust_parser_builds_tree() -> None:
    parser = RustParser()
    parsed = parser.parse(Path("main.rs"), "fn main() {}\n")
    assert parsed.language == Language.RUST
    assert parsed.ast_root is not None
    assert parsed.ast_root.root_node.type == "source_file"


def test_csharp_parser_builds_tree() -> None:
    parser = CSharpParser()
    parsed = parser.parse(Path("Program.cs"), "class Program {}\n")
    assert parsed.language == Language.CSHARP
    assert parsed.ast_root is not None


def test_generic_regex_parser_has_no_dedicated_extensions_left() -> None:
    """Every language in the initial catalog now has a dedicated AST
    parser, so the generic regex fallback's extension map is empty - it
    only exists as the landing spot for the *next* language added without
    AST support (see docs/adding-a-language.md)."""
    assert EXTENSION_TO_LANGUAGE == {}
    assert GenericRegexParser().extensions == set()
    assert not GenericRegexParser().can_parse(Path("unmapped.ext"))


def test_parsed_file_snippet_extracts_line_range() -> None:
    parser = PythonParser()
    parsed = parser.parse(Path("sample.py"), "a = 1\nb = 2\nc = 3\n")
    assert parsed.snippet(2) == "b = 2"
    assert parsed.snippet(1, 2) == "a = 1\nb = 2"


def test_registry_resolves_parser_by_extension() -> None:
    registry = ParserRegistry()
    assert isinstance(registry.get_parser_for(Path("a.py")), PythonParser)
    assert isinstance(registry.get_parser_for(Path("a.js")), JavaScriptParser)
    assert isinstance(registry.get_parser_for(Path("a.ts")), TypeScriptParser)
    assert isinstance(registry.get_parser_for(Path("a.java")), JavaParser)
    assert isinstance(registry.get_parser_for(Path("a.php")), PhpParser)
    assert isinstance(registry.get_parser_for(Path("a.go")), GoParser)
    assert isinstance(registry.get_parser_for(Path("a.rs")), RustParser)
    assert isinstance(registry.get_parser_for(Path("a.cs")), CSharpParser)
    assert registry.get_parser_for(Path("a.unknown")) is None


def test_registry_supported_extensions_covers_every_declared_language() -> None:
    registry = ParserRegistry()
    for ext in (".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".php", ".go", ".rs", ".cs"):
        assert ext in registry.supported_extensions


def test_registry_parse_returns_none_for_unsupported_file() -> None:
    registry = ParserRegistry()
    assert registry.parse(Path("a.unknown"), "content") is None
