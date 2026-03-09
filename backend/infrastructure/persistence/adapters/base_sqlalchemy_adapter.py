from abc import ABC, abstractmethod

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from ....shared.logging.logging_config import get_logger
from .database_adapter import DatabaseAdapter

logger = get_logger(__name__)


class BaseSQLAlchemyAdapter(DatabaseAdapter, ABC):
    def __init__(self) -> None:
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._engine: AsyncEngine | None = None

    @abstractmethod
    def _create_engine(self) -> AsyncEngine:
        pass

    async def connect(self) -> None:
        """Inicializar a la base de datos."""
        if self._engine is None:
            self._engine = self._create_engine()
            self._session_factory = async_sessionmaker(
                bind=self._engine, class_=AsyncSession, expire_on_commit=False
            )
            logger.info("Conexión a la base de datos establecida")

    async def disconnect(self) -> None:
        """Desconectar de la base de datos."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Conexión a la base de datos cerrada")

    async def get_session(self) -> AsyncSession:
        """Obtener una sesión asíncrona de base de datos."""
        if self._session_factory is None:
            await self.connect()
        if self._session_factory is None:
            raise RuntimeError("Conexión a la base de datos no establecida.")

        return self._session_factory()

    async def health_check(self) -> bool:
        """Comprobación del health de la conexión a la base de datos."""
        try:
            if self._engine is None:
                logger.warning("Health check fallido: engine no inicializado")
                return False

            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            logger.exception("Health check fallido")
            return False
