from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

settings = get_settings()

engine = create_async_engine(str(settings.database_url), echo=settings.debug, future=True)

session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a request-scoped SQLAlchemy async session."""
    async with session_factory() as session:
        yield session
