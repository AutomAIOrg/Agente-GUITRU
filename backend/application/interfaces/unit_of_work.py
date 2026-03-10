from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from ...domain.repositories.message_repository import MessageRepository
from ...domain.repositories.reservation_repository import ReservationRepository


class UnitOfWork(ABC):
    """
    Definicíon de patrón Unit Of Work (UoW) para gestión de transacciones
    en base de datos.
    """

    @property
    @abstractmethod
    def messages(self) -> MessageRepository:
        """Repositorio de mensajes asociado a esta unidad de trabajo."""
        pass

    @property
    @abstractmethod
    def reservations(self) -> ReservationRepository:
        """Repositorio de reservas asociado a esta unidad de trabajo."""
        pass

    @abstractmethod
    async def __aenter__(self) -> Self:
        """Abrir recursos (sesión/repositorios) y devolver UoW lista para usar."""
        pass

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Cerrar recursos y hacer rollback si se genera una excepción."""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Confirmar la transacción."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Deshacer la transacción actual si se genera una excepción."""
        pass
