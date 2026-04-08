"""PostgreSQL sans ORM — connexion async via psycopg 3."""

from app.core.config import settings
from psycopg import AsyncConnection

_conn: AsyncConnection | None = None


async def lifespan_startup() -> None:
    global _conn
    _conn = await AsyncConnection.connect(settings.database_url)


async def lifespan_shutdown() -> None:
    if _conn is not None:
        await _conn.close()


def is_database_configured() -> bool:
    return True


def get_connection() -> AsyncConnection:
    if _conn is None:
        msg = "Database not initialized"
        raise RuntimeError(msg)
    return _conn
