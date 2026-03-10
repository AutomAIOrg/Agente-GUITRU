from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from ...application.interfaces.unit_of_work import UnitOfWork
from ...domain.repositories.message_repository import MessageRepository
from ...domain.repositories.reservation_repository import ReservationRepository
from .adapters.database_adapter import DatabaseAdapter
from .sql_message_repository import SQLMessageRepository
from .sql_reservation_repository import SQLReservationRepository


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, db: DatabaseAdapter):
        self._db = db
        self._session: AsyncSession | None = None
        self._messages: MessageRepository | None = None
        self._reservations: ReservationRepository | None = None

    @property
    def messages(self) -> MessageRepository:
        if self._messages is None:
            raise RuntimeError("UoW no inicializada. Usa 'async with'.")
        return self._messages

    @property
    def reservations(self) -> ReservationRepository:
        if self._reservations is None:
            raise RuntimeError("UoW no inicializada. Usa 'async with'.")
        return self._reservations

    async def __aenter__(self) -> Self:
        """Abrir recursos (sesión/repositorios) y devolver UoW lista para usar."""
        self._session = await self._db.get_session()
        self._messages = SQLMessageRepository(db_session=self._session)
        self._reservations = SQLReservationRepository(db_session=self._session)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """Cerrar recursos y hacer rollback si se genera una excepción."""
        try:
            if exc_type is not None and self._session is not None:
                await self._session.rollback()
        finally:
            if self._session is not None:
                await self._session.close()
            self._session = None
            self._messages = None
            self._reservations = None

    async def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("Sesión en UoW no inicializada.")
        await self._session.commit()

    async def rollback(self) -> None:
        if self._session is None:
            raise RuntimeError("Sesión en UoW no inicializada.")
        await self._session.rollback()
