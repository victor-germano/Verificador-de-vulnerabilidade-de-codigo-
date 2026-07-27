# Como adicionar suporte a uma nova linguagem

Python, JavaScript, TypeScript e Java já têm parser AST dedicado
(`ast`/`tree-sitter`). PHP, Go, Rust e C# ainda passam pelo
`GenericRegexParser` (`scanner/parsers/generic_regex_parser.py`): os
arquivos são reconhecidos e roteados corretamente, mas só regras genéricas
baseadas em regex (`scanner/rules/matchers/generic/`) rodam contra eles -
sem AST. O guia abaixo usa **PHP** como exemplo; o parser Java
(`scanner/parsers/java_parser.py`) e seus matchers
(`scanner/rules/matchers/java/sql_and_command.py`) são uma referência real
já implementada do mesmo processo.

## 1. Escolha uma fonte de AST

- **tree-sitter** (recomendado): há gramáticas prontas para praticamente
  todas as linguagens do catálogo (`tree-sitter-php`, `tree-sitter-go`,
  `tree-sitter-rust`, `tree-sitter-c-sharp`). É o mesmo mecanismo já usado
  por `javascript_parser.py`/`java_parser.py` - copie um desses como ponto
  de partida, e reutilize os helpers compartilhados em
  `scanner/rules/matchers/_ts_utils.py` (`walk`, `node_text`,
  `match_from_ts_node`) - eles não são específicos de nenhuma linguagem.
- Um parser nativo do ecossistema da linguagem, se precisar de mais
  precisão semântica do que tree-sitter oferece.

## 2. Implemente o adaptador

Crie `scanner/parsers/<linguagem>_parser.py` implementando o protocolo
`LanguageParser` (`scanner/parsers/base.py`):

```python
from pathlib import Path
from app.models.enums import Language
from app.scanner.parsers.base import ParsedFile

class PhpParser:
    language = Language.PHP
    extensions = {".php"}

    def can_parse(self, path: Path) -> bool:
        return path.suffix in self.extensions

    def parse(self, path: Path, source: str) -> ParsedFile:
        # parseie `source` e devolva ParsedFile(..., ast_root=<sua árvore>)
        ...
```

## 3. Registre no `ParserRegistry`

Em `scanner/parsers/registry.py`, adicione a instância à lista
`_dedicated_parsers`, e remova a extensão de
`generic_regex_parser.EXTENSION_TO_LANGUAGE` (senão as duas entradas ficam
redundantes - a dedicada sempre ganha, mas é ruído). A partir daí, `.php`
para de cair no `GenericRegexParser` e passa a usar seu novo parser -
nenhuma outra parte do motor precisa mudar.

```python
self._dedicated_parsers = [
    PythonParser(), JavaScriptParser(), TypeScriptParser(), JavaParser(), PhpParser(),
]
```

## 4. Escreva matchers AST para essa linguagem

Crie `scanner/rules/matchers/php/`, siga o padrão de
`matchers/java/sql_and_command.py` (tree-sitter) ou
`matchers/python/_ast_utils.py` (AST nativa), e registre os matchers para
as regras cujo `languages:` já inclui `php` no YAML (ex.: `SECRET001`, que
hoje só é detectada via regex genérico, pode ganhar uma versão AST mais
precisa) - ou crie regras novas específicas da linguagem, como
`JAVASQL001`/`JAVACMD001` fizeram para Java.

Importe o novo módulo em `scanner/rules/matchers/__init__.py`.

## 5. Teste

Siga o mesmo padrão de `tests/unit/test_java_matchers.py`: um trecho
vulnerável e um seguro por regra, usando seu parser para construir o
`ParsedFile`.
