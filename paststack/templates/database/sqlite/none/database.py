"""SQLite sans ORM — connexions async via aiosqlite."""

from pathlib import Path

import aiosqlite

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH = DATA_DIR / "app.db"


async def lifespan_startup() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("SELECT 1")


async def lifespan_shutdown() -> None:
    return


def is_database_configured() -> bool:
    return True


async def get_connection() -> aiosqlite.Connection:
    """Ouvrir une connexion : `db = await get_connection()` puis `await db.close()`."""
    return await aiosqlite.connect(DB_PATH)
