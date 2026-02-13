from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession

from .infrastructure.config.settings_db import get_settings_db
from .infrastructure.persistence.adapters.database_adapter import DatabaseAdapter
from .infrastructure.persistence.adapters.mysql_adapter import MySQLAdapter


@lru_cache
def get_db_adapter() -> DatabaseAdapter:
    settings = get_settings_db()

    return MySQLAdapter(
        database_url=settings.DB_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
    )


async def get_db_session(adapter: DatabaseAdapter) -> AsyncGenerator[AsyncSession]:
    session = await adapter.get_session()
    try:
        yield session
    finally:
        session.close()
