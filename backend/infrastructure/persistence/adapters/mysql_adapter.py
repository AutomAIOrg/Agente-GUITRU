from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from .base_sqlalchemy_adapter import BaseSQLAlchemyAdapter


class MySQLAdapter(BaseSQLAlchemyAdapter):
    """MySQL database adapter using SQLAlchemy Async Engine."""

    def __init__(self, database_url: str, pool_size: int = 10, max_overflow: int = 20):
        super().__init__(
            session_factory=None
        )  # Daba error de "does not call the method of the same name in parent class (reportMissingSuperCall)"
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


# settings_db = SettingsDB()

# def _build_url_db(s: SettingsDB) -> str:
#     """Creación de la URL de conexión a la base de datos."""
#     password = urllib.parse.quote_plus(s.DB_PASS.get_secret_value())
#     return (f"mysql+asyncmy://{s.DB_USER}:{password}@{s.DB_HOST}:{s.DB_PORT}/{s.DB_NAME}")

# engine = create_async_engine(
#     _build_url_db(settings_db),
#     pool_size=settings_db.DB_POOL_SIZE,
#     max_overflow=settings_db.DB_MAX_OVERFLOW,
#     echo=False
# )

# AsyncSessionLocal = async_sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False
# )
