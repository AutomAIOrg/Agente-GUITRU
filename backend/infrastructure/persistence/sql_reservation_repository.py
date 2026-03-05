"""
Implementación de repositorio SQL para manejar reservas en la base de datos.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.reservation import Reservation
from ...domain.repositories.reservation_repository import ReservationRepository
from ...shared.logging.logging_config import get_logger
from ..models.reservation_model import ReservationModel

logger = get_logger(__name__)


class SQLReservationRepository(ReservationRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def save(self, reservation: Reservation) -> None:
        """
        Guardar un reserva en la base de datos.
        """
        logger.debug("Guardando reserva: id=%s", reservation.id)

        person_name = (
            f"{reservation.person_name.last_name}, {reservation.person_name.first_name}".strip()
        )

        # Lógica para guardar la reserva en la base de datos SQL
        db_reservation = ReservationModel(
            id=reservation.id,
            person_name=person_name,
            dni=reservation.dni.dni,
            phone_number=reservation.phone_number.phone_number,
            dates_check_in=reservation.dates_check_io.check_in,
            dates_check_out=reservation.dates_check_io.check_out,
        )

        self.db_session.add(db_reservation)

        try:
            await self.db_session.commit()
            await self.db_session.refresh(db_reservation)
            logger.debug("Reserva guardada: id=%s", reservation.id)

        except Exception as e:
            await self.db_session.rollback()
            logger.error("Error al guardar reserva id=%s: %s", reservation.id, e)
            raise
