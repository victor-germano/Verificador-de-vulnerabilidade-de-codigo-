# Como adicionar suporte a uma nova linguagem

Todas as 8 linguagens do catálogo de upload (Python, JavaScript,
TypeScript, Java, PHP, Go, Rust, C#) já têm parser AST dedicado. O guia
abaixo usa **Kotlin** como exemplo hipotético para a *próxima* linguagem;
`scanner/parsers/{java,php,go,rust,csharp}_parser.py` e seus matchers em
`scanner/rules/matchers/{java,php,go,rust,csharp}/` são referências reais
já implementadas do mesmo processo - cada uma vale a pena olhar antes de
começar, já que os detalhes de campo/nó da árvore tree-sitter variam por
gramática (ver a seção 4 abaixo).

## 1. Escolha uma fonte de AST

- **tree-sitter** (recomendado): há gramáticas prontas para praticamente
  qualquer linguagem popular (`tree-sitter-kotlin`, etc.). É o mesmo
  mecanismo já usado por todos os parsers acima - copie um deles como ponto
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

class KotlinParser:
    language = Language.KOTLIN
    extensions = {".kt"}

    def can_parse(self, path: Path) -> bool:
        return path.suffix in self.extensions

    def parse(self, path: Path, source: str) -> ParsedFile:
        # parseie `source` e devolva ParsedFile(..., ast_root=<sua árvore>)
        ...
```

(Adicionar uma linguagem nova ao catálogo também exige um novo membro em
`app.models.enums.Language` e, se for persistida em Postgres, uma migração
Alembic adicionando o valor ao tipo enum nativo `language` - ver
`alembic/versions/0001_initial.py`.)

## 3. Registre no `ParserRegistry`

Em `scanner/parsers/registry.py`, adicione a instância à lista
`_dedicated_parsers`. Se a linguagem já estivesse mapeada em
`generic_regex_parser.EXTENSION_TO_LANGUAGE`, remova a entrada de lá
(senão as duas ficam redundantes - a dedicada sempre ganha, mas é ruído).
A partir daí, a extensão para de cair no `GenericRegexParser` e passa a
usar seu novo parser - nenhuma outra parte do motor precisa mudar.

```python
self._dedicated_parsers = [
    PythonParser(), JavaScriptParser(), TypeScriptParser(), JavaParser(),
    PhpParser(), GoParser(), RustParser(), CSharpParser(), KotlinParser(),
]
```

## 4. Escreva matchers AST para essa linguagem

Crie `scanner/rules/matchers/kotlin/`, siga o padrão de
`matchers/java/sql_and_command.py` (tree-sitter) ou
`matchers/python/_ast_utils.py` (AST nativa), e registre os matchers para
as regras cujo `languages:` já inclui a linguagem no YAML (ex.:
`SECRET001`, que hoje só é detectada via regex genérico, pode ganhar uma
versão AST mais precisa) - ou crie regras novas específicas da linguagem,
como `JAVASQL001`/`PHPSQL001`/`GOSQL001`/`RUSTSQL001`/`CSHARPSQL001`
fizeram.

**Cada gramática tree-sitter tem seus próprios nomes de nó e campo** - não
assuma que o padrão de uma linguagem se aplica a outra. Por exemplo, PHP e
C# embrulham cada argumento de chamada num nó extra (`argument`) antes da
expressão real, enquanto Go e Java não. Antes de escrever o matcher, dumpe
a árvore de um trecho de exemplo (`tree_sitter.Node.child_by_field_name`,
`node.children`, `node.field_name_for_child(i)`) para confirmar a
estrutura real em vez de adivinhar.

Importe o novo módulo em `scanner/rules/matchers/__init__.py`.

## 5. Teste

Siga o mesmo padrão de `tests/unit/test_java_matchers.py` (ou
`test_php_matchers.py`/`test_go_matchers.py`/`test_rust_matchers.py`/
`test_csharp_matchers.py`): um trecho vulnerável e um seguro por regra,
usando seu parser para construir o `ParsedFile`.
