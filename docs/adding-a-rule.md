# Como adicionar uma nova regra

Uma regra tem duas partes independentes: **metadados** (YAML) e
**detecção** (código Python). Nenhuma das duas exige tocar no motor
(`scanner/engines/`).

## 1. Metadados

Crie `backend/app/scanner/rules/definitions/<id-em-minusculas>.yaml`
seguindo o schema `Rule` (`scanner/rules/schema.py`):

```yaml
id: CMD002
name: Command Injection via Popen shell=True
description: >
  Descrição do que a vulnerabilidade é e por que é perigosa.
category: Injection
owasp: "A03:2021 - Injection"
cwe: CWE-78
cvss: 9.8
severity: critical       # critical | high | medium | low | info
confidence: medium        # high | medium | low (default se o matcher não sobrescrever)
languages: [python]       # uma ou mais linguagens de app.models.enums.Language
message: >
  Frase curta explicando o problema (aparece como "explicação técnica").
recommendation: >
  Como corrigir.
vulnerable_example: |
  codigo_vulneravel()
secure_example: |
  codigo_corrigido()
references:
  - "https://cwe.mitre.org/data/definitions/78.html"
```

Isso sozinho já deixa a regra visível no catálogo (`get_rules()`), mas sem
nenhum matcher ela nunca vai gerar findings - o `Detector` ignora
silenciosamente regras sem matcher registrado.

## 2. Detecção (matcher)

Um matcher é uma função `ParsedFile -> list[MatchResult]`, registrada contra
o `id` da regra:

```python
from app.scanner.parsers.base import ParsedFile
from app.scanner.rules.matcher_registry import MatchResult, register_matcher

@register_matcher("CMD002")
def match_popen_shell_true(parsed: ParsedFile) -> list[MatchResult]:
    if parsed.ast_root is None:
        return []
    # ... percorra parsed.ast_root e devolva um MatchResult por ocorrência
```

Onde colocar a função:

- **Python** (`ast.Module`): `scanner/rules/matchers/python/`. Use os
  helpers de `_ast_utils.py` (`find_calls`, `get_call_name`,
  `is_dynamic_string`, `match_from_node`).
- **JavaScript/TypeScript** (`tree_sitter.Tree`):
  `scanner/rules/matchers/javascript/`. Use os helpers de `_ts_utils.py`
  (`walk`, `node_text`, `match_from_ts_node`).
- **Regex, multi-linguagem** (roda em qualquer `ParsedFile`, inclusive
  linguagens sem AST): `scanner/rules/matchers/generic/`. Use
  `find_regex_matches` de `_regex_utils.py`.

Depois, importe o módulo em `scanner/rules/matchers/__init__.py` (se criou
um arquivo novo) para que o `@register_matcher` seja executado no startup.

## 3. Teste

Adicione um teste em `tests/unit/test_python_matchers.py` (ou o arquivo
equivalente para JS/generic) cobrindo pelo menos:

- um trecho vulnerável → 1+ `MatchResult`;
- um trecho seguro equivalente → lista vazia.

```python
def test_popen_shell_true_flags_dynamic_command() -> None:
    vulnerable = "subprocess.Popen(cmd, shell=True)\n"
    assert len(_matches("CMD002", vulnerable)) == 1
```

Pronto - a regra aparece no catálogo, é detectada, e conta para o Security
Score automaticamente (`RiskCalculator` já pondera por severidade).
