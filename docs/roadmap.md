# Roadmap

## Entregue

- Backend FastAPI + SQLAlchemy async + Alembic, Clean Architecture.
- Scanner engine: parsers com AST real para Python (`ast`), JavaScript/
  TypeScript e Java (`tree-sitter`); fallback regex para PHP/Go/Rust/C#.
  Rule engine orientado a dados (YAML + matchers), risk calculator,
  geradores de relatório (JSON/Markdown/HTML/PDF).
- **30 regras** cobrindo SQL/NoSQL/Command/Code/LDAP/XPath Injection,
  Server-Side Template Injection, Path Traversal, SSRF, Insecure
  Deserialization, XXE, XSS refletido/DOM, Insecure Cookie, Open Redirect,
  Weak Crypto (hash e cifra), Weak Random, Hardcoded Password/Secret,
  Sensitive Logging, Unsafe File Upload, Unsafe Reflection, File Inclusion,
  Resource Leak, Insecure Temporary Files - incluindo variantes específicas
  para Java (`JAVASQL001`, `JAVACMD001`) e Node.js (`JSCMD001`).
- Três formas de escanear: upload de arquivo/pasta `.zip`, repositório Git
  público (clone shallow via GitPython) e CLI standalone (`sast-cli`).
- API REST com auth JWT, rate limiting, CORS, security headers, tratamento
  global de exceções.
- Frontend React com dashboard (gráficos, score, tendência), upload/scan,
  scan de repositório Git, findings com filtros e paginação, notificações
  (toast) de resultado de scan, tema claro/escuro, code-splitting por rota.
- Docker Compose (Postgres + backend + frontend via nginx).
- CI (GitHub Actions): lint + testes com gate de cobertura (backend),
  lint + build (frontend), em todo push/PR.
- Suíte de testes (unit + integração), 150+ testes, cobertura ~95%.

## Próximos passos (não implementado ainda)

Itens abaixo têm pontos de extensão já preparados no código (ver
`docs/architecture.md`), mas nenhuma implementação funcional ainda:

- **IA**: `scanner/ai/analyzer.py` define a interface `AIAnalyzer`
  (`explain`, `suggest_fix`, `summarize`). Implementar uma classe concreta
  (ex. `OpenAIAnalyzer`) e trocar `get_ai_analyzer()` é o único passo
  necessário para ligar essa funcionalidade.
- **Execução assíncrona / fila**: `workers/task_queue.py` define o
  protocolo `TaskQueue`; hoje só existe `InProcessTaskQueue` (roda dentro do
  processo da API). Trocar por Celery/RQ + Redis não exige mudanças em
  `ScanService` nem na API.
- **Deploy automático em CI/CD**: o workflow atual (`.github/workflows/ci.yml`)
  cobre lint + testes + build; falta um job de deploy (build e push de
  imagem Docker, deploy em um ambiente).
- **Análise automática de Pull Requests**: comentar findings diretamente em
  PRs do GitHub/GitLab/Bitbucket.
- **Autenticação Git privada**: hoje só repositórios públicos via
  `http(s)://` são suportados (`utils/git_handling.py`); repositórios
  privados exigiriam suporte a token/SSH, deliberadamente fora de escopo
  por ora (superfície de risco maior - credenciais de terceiros).
- **Plugins de IDE** (VS Code, JetBrains).
- **API pública** com chaves de API dedicadas (hoje a API é apenas para o
  frontend, autenticada por JWT de usuário).
- **Modo Enterprise**: multiempresa, sistema de permissões/papéis, SSO.
- **Webhooks e notificações externas** (e-mail/Slack) ao final de um scan
  (o frontend já notifica o próprio usuário via toast em tempo real).
- **Cache com Redis** para consultas de dashboard sob carga.
- **Execução distribuída / escalabilidade horizontal** dos workers de scan.
- Parsers AST dedicados para PHP, Go, Rust e C# (hoje: Python, JS, TS, Java
  - ver `docs/adding-a-language.md`) e mais regras no catálogo (ver
  `docs/adding-a-rule.md`).
