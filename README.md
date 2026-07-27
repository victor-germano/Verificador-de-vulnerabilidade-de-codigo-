# SAST Platform

[![CI](https://github.com/vgermano1711/Verificador-de-vulnerabilidade-de-codigo-/actions/workflows/ci.yml/badge.svg)](https://github.com/vgermano1711/Verificador-de-vulnerabilidade-de-codigo-/actions/workflows/ci.yml)

Plataforma de análise estática de código (**SAST — Static Application
Security Testing**) para identificar vulnerabilidades de segurança em
projetos de código-fonte, com engine de regras extensível, suporte
multi-linguagem, dashboard de risco e relatórios exportáveis.

## Objetivo

Analisar um projeto (arquivo, pasta `.zip` ou repositório Git público) e
produzir, para cada vulnerabilidade encontrada: localização exata,
severidade, explicação técnica, impacto, nível de confiança, recomendação de
correção e um exemplo de código seguro — com metadados de OWASP, CWE e CVSS.
Ver [`docs/architecture.md`](docs/architecture.md) para o desenho completo.

## Funcionalidades

- **30 regras de detecção** cobrindo Injection (SQL/NoSQL/Command/Code/LDAP/
  XPath/SSTI), Insecure Deserialization, XXE, SSRF, XSS (refletido e DOM),
  Path Traversal, Unsafe File Upload, Unsafe Reflection, File Inclusion,
  Resource Leak, Insecure Temporary Files, criptografia fraca, segredos
  hardcoded, cookies inseguros, open redirect e logging sensível.
- **Análise via AST real** para Python (`ast`), JavaScript/TypeScript e Java
  (`tree-sitter`) — não apenas regex. Demais linguagens do upload
  (PHP/Go/Rust/C#) usam regras genéricas por regex até ganharem parser
  dedicado (ver [`docs/adding-a-language.md`](docs/adding-a-language.md)).
- **Três formas de escanear**: upload de arquivo/pasta `.zip`, repositório
  Git público (`https://…git`) ou linha de comando (`sast-cli`).
- **Security Score**, tendência histórica, top vulnerabilidades/arquivos no
  dashboard.
- **Relatórios** em JSON, Markdown, HTML e PDF.
- **CLI standalone** (`sast-cli`) que roda o mesmo motor sem precisar de API
  nem banco de dados — útil em pipelines de CI de outros projetos.

## Stack

| Camada | Tecnologias |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2 (async), Alembic, Pydantic |
| Scanner engine | `ast` (Python), `tree-sitter` (JS/TS/Java), GitPython, regras em YAML |
| Banco | PostgreSQL |
| Frontend | React, TypeScript, Vite, Tailwind CSS v4, Radix UI, TanStack Query, React Hook Form, Zod, Recharts |
| Infra | Docker, Docker Compose, nginx |

## Estrutura do repositório

```
root/
├── backend/     API + scanner engine (ver backend/app/...)
├── frontend/    SPA React
├── docker/      Dockerfiles e nginx.conf
├── docs/        Documentação detalhada (arquitetura, como estender)
└── scripts/     Scripts de bootstrap
```

## Como rodar

### Opção A — Docker Compose (recomendado)

```bash
cp .env.example .env   # ajuste SECRET_KEY antes de ir para produção
docker compose up --build
```

- Frontend: http://localhost:8080
- API: http://localhost:8000 (docs interativas em `/api/docs`)
- Postgres: `localhost:5432` (usuário/senha/banco `sast`)

As migrações do Alembic rodam automaticamente no start do container do
backend.

### Opção B — Desenvolvimento local (sem Docker)

Pré-requisitos: Python 3.12+, Node 20+, PostgreSQL rodando localmente (ou
via `docker compose up postgres`).

```bash
./scripts/setup.sh   # cria o venv, instala deps do backend e do frontend
```

Ou manualmente:

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # .venv/Scripts/activate no Windows
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload

# Frontend (em outro terminal)
cd frontend
npm install
npm run dev
```

O Vite já vem configurado para fazer proxy de `/api` para
`http://localhost:8000` (`frontend/vite.config.ts`), então basta abrir
http://localhost:5173.

## Banco de dados

Modelo relacional: `users` → `projects` → `scans` → `findings` (ver
`backend/app/models/`). Migrações ficam em `backend/alembic/versions/`.

```bash
cd backend
alembic upgrade head                              # aplicar migrações
alembic revision --autogenerate -m "descrição"     # gerar uma nova migração
```

## CLI standalone

Roda o mesmo motor de análise sem precisar da API nem de um banco de dados
- útil para rodar em CI de outros projetos ou localmente:

```bash
cd backend
pip install -e .
sast-cli /caminho/do/projeto --format markdown --output relatorio.md
sast-cli /caminho/do/projeto --fail-on high   # sai com código 1 se achar algo >= high
```

## Testes

```bash
cd backend
pytest --cov --cov-report=term-missing
```

O gate de cobertura (90%, configurado em `backend/pyproject.toml`) cobre os
módulos de `scanner/`, `services/`, `repositories/` e `security/`.

```bash
cd frontend
npm run build   # type-check (tsc -b) + build de produção
npm run lint
```

## Qualidade de código

```bash
cd backend
black app tests
isort app tests
ruff check app tests --fix
pre-commit install   # roda essas checagens automaticamente antes de cada commit
```

Padrão de commits: [Conventional Commits](https://www.conventionalcommits.org/)
(`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, ...).

## Como estender

- **Adicionar uma regra de detecção** → [`docs/adding-a-rule.md`](docs/adding-a-rule.md)
- **Adicionar suporte a uma linguagem** → [`docs/adding-a-language.md`](docs/adding-a-language.md)
- **Entender o fluxo interno de um scan** → [`docs/architecture.md`](docs/architecture.md)

## Como contribuir

1. Crie uma branch a partir de `main`.
2. Rode `black`, `isort`, `ruff` (backend) e `npm run lint` (frontend) antes
   de abrir o PR — o `pre-commit` automatiza isso.
3. Adicione testes cobrindo a mudança (matcher novo → teste com trecho
   vulnerável e trecho seguro; endpoint novo → teste de integração).
4. Descreva no PR o *porquê* da mudança, não só o *o quê*.

## Roadmap

O que já está implementado e o que é ponto de extensão preparado mas ainda
não implementado (IA, plugins de IDE, multi-tenant, execução distribuída,
etc.): [`docs/roadmap.md`](docs/roadmap.md).

## Licença

[MIT](LICENSE).
