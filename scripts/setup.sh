#!/usr/bin/env bash
# Bootstraps a local development environment (no Docker): creates the
# backend virtualenv, installs both backend and frontend dependencies, and
# copies .env.example to .env if it doesn't exist yet.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -f "$ROOT_DIR/.env" ]; then
  cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
  echo "Created .env from .env.example - review it before running the app."
fi

echo "Setting up backend..."
cd "$ROOT_DIR/backend"
python -m venv .venv
if [ -f ".venv/Scripts/activate" ]; then
  source .venv/Scripts/activate # Windows
else
  source .venv/bin/activate # Linux/macOS
fi
pip install --upgrade pip
pip install -e ".[dev]"
pre-commit install || true

echo "Setting up frontend..."
cd "$ROOT_DIR/frontend"
npm install

echo "Done. Next steps:"
echo "  1) Start Postgres (docker compose up postgres, or your own instance)"
echo "  2) cd backend && alembic upgrade head"
echo "  3) cd backend && uvicorn app.main:app --reload"
echo "  4) cd frontend && npm run dev"
