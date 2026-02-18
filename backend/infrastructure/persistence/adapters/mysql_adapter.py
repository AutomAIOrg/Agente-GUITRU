from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from .base_sqlalchemy_adapter import BaseSQLAlchemyAdapter


class MySQLAdapter(BaseSQLAlchemyAdapter):
    """MySQL database adapter using SQLAlchemy Async Engine."""

    def __init__(self, database_url: str, pool_size: int = 10, max_overflow: int = 20):
        super().__init__(session_factory=None)
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow

    def _create_engine(self) -> AsyncEngine:
        """Crear el motor AsyncEngine para la conexión a la base de datos MySQL."""
        return create_async_engine(
            self.database_url, pool_size=self.pool_size, max_overflow=self.max_overflow, echo=False
        )

    async def connect(self) -> None:
        """Inicializar conexión a la base de datos MySQL y creación de tablas."""
        await super().connect()

        if self._engine is not None:
            async with self._engine.begin() as conn:
                from ...models.base import Base

                await conn.run_sync(Base.metadata.create_all)
