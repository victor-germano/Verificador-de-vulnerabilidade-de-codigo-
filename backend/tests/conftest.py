from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.api import deps as api_deps
from app.config.settings import Settings
from app.database.base import Base
from app.database.session import get_db_session
from app.main import app
from app.security.rate_limiter import limiter


@pytest.fixture(autouse=True)
def _reset_rate_limiter() -> None:
    """slowapi's in-memory limiter storage is process-wide, not per-test -
    without a reset, tests that call /auth/register or /auth/login (rate
    limited to 10/minute) start failing once enough other tests in the same
    run have exercised those endpoints, in an order-dependent way."""
    limiter.reset()


@pytest.fixture(autouse=True)
def _disable_ai_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests must never depend on ambient environment variables - if this
    sandbox happens to have an `ANTHROPIC_API_KEY` set (e.g. for the coding
    agent's own use), `get_ai_analyzer()` would otherwise pick it up and
    make real, billed calls to the Anthropic API during a routine test run.
    Individual tests (see test_api_deps.py) can still monkeypatch
    `api_deps.get_settings` themselves to exercise the AI-enabled path."""
    api_deps.get_ai_analyzer.cache_clear()
    monkeypatch.setattr(api_deps, "get_settings", lambda: Settings(anthropic_api_key=None))
    yield
    api_deps.get_ai_analyzer.cache_clear()


@pytest_asyncio.fixture
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_engine: AsyncEngine) -> AsyncGenerator[AsyncClient, None]:
    session_factory = async_sessionmaker(bind=db_engine, expire_on_commit=False)

    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


FIXTURES_DIR = Path(__file__).parent / "fixtures"
