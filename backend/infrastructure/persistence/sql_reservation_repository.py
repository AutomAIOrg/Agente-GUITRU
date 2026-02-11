"""
Implementación de repositorio SQL para manejar los mensajes en la base de datos.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.reservation import Reservation
from ...domain.repositories.reservation_repository import ReservationRepository
from .models.reservations_model import ReservationsModel


class SQLReservationRepository(ReservationRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def save(self, reservation: Reservation) -> None:
        """
        Guardar un reserva en la base de datos.
        """
        # Lógica para guardar la reserva en la base de datos SQL
        db_reservation = ReservationsModel(
            id=reservation.id,
            person_name=reservation.person_name,
            dni=reservation.dni,
            phone_number=reservation.phone_number,
            dates_check_in=reservation.dates_check_io.check_in,
            dates_check_out=reservation.dates_check_io.check_out,
        )

        self.db_session.add(db_reservation)

        try:
            await self.db_session.commit()
            await self.db_session.refresh(db_reservation)

        except Exception as e:
            await self.db_session.rollback()
            print(f"Error saving reservation: {e}")
            raise e
