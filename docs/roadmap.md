# Roadmap

## Entregue

- Backend FastAPI + SQLAlchemy async + Alembic, Clean Architecture.
- Scanner engine: **parser AST real para as 8 linguagens do catálogo** -
  Python (`ast` nativo) e JavaScript/TypeScript/Java/PHP/Go/Rust/C#
  (`tree-sitter`). Nenhuma linguagem do catálogo depende só de regex mais -
  `GenericRegexParser` fica como base para a próxima linguagem além dessas
  8 (ver `docs/adding-a-language.md`). Rule engine orientado a dados (YAML +
  matchers), risk calculator, geradores de relatório (JSON/Markdown/HTML/PDF).
- **38 regras** cobrindo SQL/NoSQL/Command/Code/LDAP/XPath Injection,
  Server-Side Template Injection, Path Traversal, SSRF, Insecure
  Deserialization, XXE, XSS refletido/DOM, Insecure Cookie, Open Redirect,
  Weak Crypto (hash e cifra), Weak Random, Hardcoded Password/Secret,
  Sensitive Logging, Unsafe File Upload, Unsafe Reflection, File Inclusion,
  Resource Leak, Insecure Temporary Files - incluindo variantes de SQL/
  Command Injection específicas por linguagem para Java (`JAVASQL001`,
  `JAVACMD001`), PHP (`PHPSQL001`, `PHPCMD001`), Go (`GOSQL001`,
  `GOCMD001`), Rust (`RUSTSQL001`, `RUSTCMD001`), C# (`CSHARPSQL001`,
  `CSHARPCMD001`) e Node.js (`JSCMD001`).
- Validado contra um repositório real de grande porte (OWASP Juice Shop,
  644 arquivos) rodando no Docker Compose de produção: 188 vulnerabilidades
  encontradas em ~5s.
- Três formas de escanear: upload de arquivo/pasta `.zip`, repositório Git
  público (clone shallow via GitPython) e CLI standalone (`sast-cli`).
- API REST com auth JWT, rate limiting, CORS, security headers, tratamento
  global de exceções.
- Frontend React com dashboard (gráficos, score, tendência), upload/scan,
  scan de repositório Git, findings com filtros e paginação, notificações
  (toast) de resultado de scan, tema claro/escuro, code-splitting por rota.
- Docker Compose (Postgres + backend + frontend via nginx).
- CI (GitHub Actions): lint + testes com gate de cobertura (backend),
  lint + build (frontend), em todo push/PR; job `docker-publish` faz build
  e push das imagens de backend/frontend para o GHCR
  (`ghcr.io/<repo>-backend`/`-frontend`, tags `latest` e `<sha>`) usando o
  `GITHUB_TOKEN` automático - sem segredos externos a configurar.
- **IA (Anthropic)**: `scanner/ai/analyzer.py` define a interface
  `AIAnalyzer`; `AnthropicAIAnalyzer` (`scanner/ai/anthropic_analyzer.py`)
  é a implementação concreta usando o SDK oficial `anthropic`. Endpoints
  `POST /api/v1/ai/findings/{id}/explain`, `/suggest-fix` e
  `/scans/{id}/summarize` explicam um finding, sugerem uma correção
  concreta e resumem um scan inteiro em português. Sem `ANTHROPIC_API_KEY`
  configurada, os endpoints respondem `501 Not Implemented`
  (`NullAIAnalyzer`) em vez de falhar - a funcionalidade é opcional e
  gracioso na ausência de chave.
- **Autenticação Git privada**: `POST /api/v1/scans/git` aceita um
  `access_token` opcional, injetado como header `Authorization: bearer`
  via `git -c http.extraheader=...` (nunca embutido na URL, para não
  vazar em logs) - suporta repositórios privados do GitHub/GitLab/Bitbucket
  com personal access token (`utils/git_handling.py`).
- **Colaboração por projeto**: cada projeto tem um dono (`owner_id`) e uma
  lista de colaboradores (`ProjectCollaborator`) com papel `editor` ou
  `viewer`. Donos e editores podem rodar scans; viewers só visualizam;
  apenas o dono gerencia colaboradores e apaga o projeto
  (`ProjectService.require_editor`/`require_owner`). Endpoints em
  `GET/POST /api/v1/projects/{id}/collaborators` e
  `PATCH/DELETE /api/v1/projects/{id}/collaborators/{user_id}`; UI de
  gestão de colaboradores no frontend (`features/collaborators/`).
- Suíte de testes (unit + integração), 200+ testes, cobertura ~94%.

## Próximos passos (não implementado ainda)

Itens abaixo têm pontos de extensão já preparados no código (ver
`docs/architecture.md`), mas nenhuma implementação funcional ainda:

- **Execução assíncrona / fila**: `workers/task_queue.py` define o
  protocolo `TaskQueue`; hoje só existe `InProcessTaskQueue` (roda dentro do
  processo da API). Trocar por Celery/RQ + Redis não exige mudanças em
  `ScanService` nem na API.
- **Deploy automático em ambiente vivo**: o CI já publica imagens no GHCR
  (ver acima); falta um job que faça deploy dessas imagens em um ambiente
  (Kubernetes, um VPS via SSH, Fly.io, etc.) - decisão de infraestrutura
  que depende de onde o produto vai rodar.
- **Análise automática de Pull Requests**: comentar findings diretamente em
  PRs do GitHub/GitLab/Bitbucket.
- **Plugins de IDE** (VS Code, JetBrains).
- **API pública** com chaves de API dedicadas (hoje a API é apenas para o
  frontend, autenticada por JWT de usuário).
- **Modo Enterprise completo**: SSO, organizações com múltiplos times e
  faturamento - a colaboração por projeto (ver acima) cobre o caso de uso
  de equipes pequenas/médias compartilhando projetos; uma camada de
  Organization acima de `User`/`Project` seria o próximo passo se surgir
  demanda por isolamento entre múltiplas empresas na mesma instância.
- **Webhooks e notificações externas** (e-mail/Slack) ao final de um scan
  (o frontend já notifica o próprio usuário via toast em tempo real).
- **Cache com Redis** para consultas de dashboard sob carga.
- **Execução distribuída / escalabilidade horizontal** dos workers de scan.
- Mais linguagens além das 8 já cobertas (Kotlin, Swift, Ruby, ...) e mais
  regras no catálogo (ver `docs/adding-a-rule.md` e
  `docs/adding-a-language.md`).
