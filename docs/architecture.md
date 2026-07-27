# Arquitetura

## Visão geral

O projeto é um monorepo com dois componentes principais:

```
root/
├── backend/    FastAPI + SQLAlchemy + scanner engine (Python) + CLI standalone
├── frontend/   React + TypeScript + Vite
├── docker/     Dockerfiles e configuração de nginx
├── docs/       Esta pasta
├── .github/    Workflow de CI (lint + testes + build)
└── scripts/    Scripts de bootstrap
```

O `scanner/` (motor de análise) é consumido por dois pontos de entrada
independentes: a API (`ScanService`, via upload ou clone de repositório
Git) e a CLI standalone (`app/cli.py`, `sast-cli`) - nenhum dos dois
importa código do outro, ambos só dependem de `app.scanner`.

O backend segue **Clean Architecture**: cada camada só conhece a camada
imediatamente abaixo dela, e a lógica de negócio (scanner engine, regras,
cálculo de score) não depende de FastAPI nem de SQLAlchemy.

```
app/
├── api/            Camada de entrega HTTP (FastAPI routers, dependências)
├── services/        Casos de uso / orquestração (camada de aplicação)
├── repositories/      Acesso a dados (Protocols + implementações SQLAlchemy)
├── models/             ORM (SQLAlchemy) - estado persistido
├── schemas/             DTOs (Pydantic) - contratos da API
├── scanner/               Domínio: motor de análise estática (framework-agnostic)
│   ├── parsers/              Adaptadores de linguagem -> AST
│   ├── engines/                Scanner, Detector, Analyzer, RiskCalculator
│   ├── rules/                    Catálogo de regras (YAML) + matchers (código)
│   ├── reports/                    Geradores de relatório (JSON/MD/HTML/PDF)
│   └── ai/                          AIAnalyzer (interface) + AnthropicAIAnalyzer + NullAIAnalyzer
├── security/         JWT, hashing de senha, rate limiting, security headers
├── workers/           Interface de fila de tarefas (execução assíncrona futura)
├── core/               Exceções de domínio, logging estruturado
├── config/              Settings (pydantic-settings)
└── database/             Engine/sessão SQLAlchemy async
```

A regra de dependência: `api` → `services` → `repositories`/`scanner` →
`models`/`schemas`. Nada em `scanner/` importa FastAPI, SQLAlchemy ou
qualquer coisa de `api/`.

## Fluxo de uma análise (scan)

1. O usuário envia um arquivo (ou `.zip`) via `POST /api/v1/scans/upload`,
   ou uma URL de repositório Git público via `POST /api/v1/scans/git`.
2. `api/v1/scans.py` prepara o diretório a ser escaneado - salva o upload
   (`utils/file_handling.py`, com proteção contra zip slip) ou clona o
   repositório (`utils/git_handling.py`, clone shallow restrito a
   `http(s)://` para evitar SSRF/argument injection) - e delega para
   `ScanService.run_scan`.
3. `ScanService` cria o registro `Scan` (status `running`) e chama
   `ScannerEngine.scan_path`, que:
   - percorre os arquivos do alvo (`_iter_target_files`);
   - resolve o parser certo por extensão (`ParserRegistry`);
   - roda todas as regras aplicáveis àquela linguagem (`Detector` +
     `RuleEngine`), usando o matcher registrado para cada `rule.id`
     (`matcher_registry`);
   - agrega os resultados em `DetectedFinding` (`Analyzer`), com
     deduplicação;
   - calcula o Security Score (`RiskCalculator`).
4. `ScanService` persiste os `Finding`s e atualiza o `Scan` para `completed`
   (ou `failed`, preservando a mensagem de erro).
5. O frontend consulta `/api/v1/scans/{id}`, `/api/v1/findings` e
   `/api/v1/dashboard/*` via TanStack Query para refletir o resultado.

## Motor de regras (Rule Engine)

Ponto central de extensibilidade do produto - ver [`adding-a-rule.md`](./adding-a-rule.md).

- **Metadados** (id, nome, severidade, OWASP, CWE, CVSS, exemplos,
  referências) vivem em YAML (`scanner/rules/definitions/*.yaml`),
  validados pelo schema Pydantic `Rule`.
- **Detecção** (como encontrar a vulnerabilidade) vive em código Python,
  registrado contra o `rule.id` via `@register_matcher("SQL001")`
  (`scanner/rules/matcher_registry.py`).
- O `RuleEngine` só lida com metadados; o `Detector` só lida com "qual
  matcher rodar"; nenhum dos dois conhece a lógica de detecção em si.

Isso significa que uma regra pode ser documentada no catálogo sem ainda ter
detecção implementada (fica apenas sem matcher registrado, e o `Detector`
simplesmente a ignora) - útil para planejar o roadmap de cobertura sem
quebrar nada.

## Parsers e AST

Cada linguagem tem um adaptador que implementa o protocolo `LanguageParser`
(`scanner/parsers/base.py`) e devolve um `ParsedFile` com:

- Python: `ast.Module` nativo (`python_parser.py`).
- JavaScript/TypeScript/Java/PHP/Go/Rust/C#: árvore do `tree-sitter`
  (`javascript_parser.py`/`typescript_parser.py`/`java_parser.py`/
  `php_parser.py`/`go_parser.py`/`rust_parser.py`/`csharp_parser.py`), com
  helpers de percurso compartilhados entre todas em
  `scanner/rules/matchers/_ts_utils.py` (não são específicos de nenhuma
  linguagem - percorrem qualquer `tree_sitter.Tree`).

Todas as 8 linguagens do catálogo de upload têm parser AST dedicado -
`GenericRegexParser` (`ast_root=None`, só regras regex) fica como a
implementação padrão para a *próxima* linguagem adicionada sem AST ainda.
Ver [`adding-a-language.md`](./adding-a-language.md) para o processo.

## Segurança implementada

- Senhas com `bcrypt` (`security/password.py`).
- JWT de acesso/refresh (`security/jwt.py`), validados por
  `api/deps.get_current_user`.
- Rate limiting por IP (`slowapi`) nos endpoints de autenticação.
- Cabeçalhos de segurança padrão em toda resposta
  (`security/headers_middleware.py`).
- CORS restrito à origem do frontend (configurável via `CORS_ALLOW_ORIGINS`).
- Tratamento global de exceções: erros de domínio (`core/exceptions.py`)
  viram respostas HTTP consistentes; erros não tratados nunca vazam stack
  trace para o cliente.
- Proteção contra zip slip na extração de uploads `.zip`.
- Clone de repositório Git restrito a URLs `http(s)://` (sem `file://`/SSH)
  e rejeição de URLs iniciadas por `-` (argument injection no binário
  `git`) - `utils/git_handling.py`. Repositórios privados são suportados
  via um `access_token` opcional, validado contra um charset restrito e
  injetado como header `Authorization` via `git -c http.extraheader=...`
  (nunca embutido na URL) - se o clone falhar, o token é redigido
  (`***`) antes da mensagem de erro chegar ao cliente.

## IA (opcional)

`scanner/ai/analyzer.py` define o protocolo `AIAnalyzer` (`explain`,
`suggest_fix`, `summarize`). `AnthropicAIAnalyzer`
(`scanner/ai/anthropic_analyzer.py`) é a implementação real, usando o SDK
oficial `anthropic`. `api/deps.get_ai_analyzer()` (com `@lru_cache`) decide
em runtime qual implementação injetar:

- `ANTHROPIC_API_KEY` configurada → `AnthropicAIAnalyzer`.
- Sem chave → `NullAIAnalyzer`, cujos métodos levantam `NotImplementedError`.

`AIService` (`services/ai_service.py`) converte esse `NotImplementedError`
em `FeatureNotConfiguredError` (HTTP 501) - os endpoints de IA
(`api/v1/ai.py`) sempre respondem de forma previsível, mesmo sem chave
configurada. A checagem de autorização (`_authorize_finding_access`) segue
a mesma cadeia finding → scan → project → papel do usuário usada no resto
da API.

## Colaboração por projeto

Cada `Project` tem um `owner_id` (acesso total implícito) e uma lista de
`ProjectCollaborator` (papel `editor` ou `viewer`), sem um modelo de
Organization/multiempresa completo - decisão deliberada para cobrir o caso
de uso de times pequenos compartilhando projetos sem a complexidade de
isolamento entre empresas.

- `ProjectService.get_role(user_id, project)` resolve o papel efetivo do
  usuário (`"owner"` | `ProjectRole`) e é a base de `require_editor`
  (dono ou editor - necessário para rodar scans) e `require_owner` (só o
  dono - necessário para apagar o projeto ou gerenciar colaboradores).
- `ProjectRepository.list_accessible_to`/`DashboardRepository` usam uma
  subquery `OR` (`owner_id == user OR id IN (projetos onde é colaborador)`)
  para que a listagem de projetos e o dashboard incluam projetos
  colaborados, não só os próprios.
- Endpoints em `api/v1/projects.py`:
  `GET/POST /projects/{id}/collaborators`,
  `PATCH/DELETE /projects/{id}/collaborators/{user_id}`.

## Frontend

- **Roteamento**: `react-router-dom`, com `ProtectedRoute` guardando as
  rotas autenticadas e `AuthProvider` resolvendo o usuário atual a partir do
  token salvo em `localStorage`.
- **Dados remotos**: `@tanstack/react-query` por feature
  (`features/<nome>/{api.ts,hooks.ts}`), com `axios` configurado para
  injetar o Bearer token e redirecionar para `/login` em um 401.
- **UI**: componentes no estilo shadcn/ui (Radix primitives + Tailwind v4 +
  `class-variance-authority`) em `components/ui/`, tema claro/escuro via
  CSS custom properties (`index.css`) e `ThemeProvider`.
- **Gráficos**: Recharts, com cores fixas por severidade
  (`lib/chart-colors.ts`) - atributos de preenchimento SVG não resolvem
  `var()` com a mesma confiabilidade que CSS comum, então cores de
  severidade usam hexadecimais fixos.
- **Code-splitting**: cada página é importada via `React.lazy` em `App.tsx`,
  então bibliotecas pesadas usadas só em uma rota (ex.: Recharts no
  Dashboard) não entram no bundle inicial.
- **Feedback de ações**: `sonner` (`<Toaster />` em `main.tsx`) para
  notificações de sucesso/erro de scans e criação de projetos; a tabela de
  findings pagina no cliente (20 por página) para não renderizar centenas
  de linhas de uma vez.
- **Colaboradores**: `features/collaborators/CollaboratorsCard.tsx` (usado
  em `pages/ProjectDetail.tsx`) lista, adiciona, atualiza o papel e remove
  colaboradores de um projeto. Ações de gestão só aparecem para o dono
  (`project.owner_id === user.id`); o botão de novo scan também é ocultado
  para quem tem papel `viewer`, refletindo no cliente a mesma regra já
  aplicada pelo backend.
