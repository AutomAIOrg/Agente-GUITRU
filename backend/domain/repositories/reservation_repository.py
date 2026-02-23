"""
Repositorio para manejar las reservas en la base de datos.
"""

from abc import ABC, abstractmethod

from ...domain.entities.reservation import Reservation


class ReservationRepository(ABC):
    @abstractmethod
    async def save(self, reservation: Reservation) -> None:
        """
        Guardar una reserva en la base de datos.
        """
        pass
