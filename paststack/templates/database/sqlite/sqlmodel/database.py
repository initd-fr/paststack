"""SQLite + SQLModel (async)."""

from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.core.config import settings

engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
)
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def lifespan_startup() -> None:
    (Path(__file__).resolve().parent.parent.parent / "data").mkdir(parents=True, exist_ok=True)
    import app.models  # noqa: F401 — pour enregistrer les tables auprès de SQLModel

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def lifespan_shutdown() -> None:
    await engine.dispose()


def is_database_configured() -> bool:
    return True


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
