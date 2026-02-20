from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.domain.entities.reservation import Reservation
from backend.domain.value_objects.dates_io import DatesIO
from backend.domain.value_objects.dni import DNI
from backend.domain.value_objects.person_name import PersonName
from backend.domain.value_objects.phone_number import PhoneNumber
from backend.infrastructure.persistence.sql_reservation_repository import SQLReservationRepository

pytestmark = [
    pytest.mark.unit,
    pytest.mark.asyncio,
]


async def test_save_reservation():
    # Mock AsyncSession
    mock_session = AsyncMock()

    # Crear instancia del repositorio
    repository = SQLReservationRepository(mock_session)

    # Crear una reserva de prueba
    reservation = Reservation(
        id=str(uuid4()),
        person_name=PersonName(first_name="John", last_name="Doe"),
        dni=DNI("12345678A"),
        phone_number=PhoneNumber(phone_number="+12345678901"),
        dates_check_io=DatesIO(
            check_in=datetime.now(),
            check_out=datetime.now() + timedelta(days=1),
        ),
    )

    # Ejecutar el método save
    await repository.save(reservation)

    # Verificar que se llamaron los métodos correctos
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


async def test_save_reservation_rollback_on_error():
    # Mock AsyncSession
    mock_session = AsyncMock()
    mock_session.commit.side_effect = Exception("Database error")

    # Crear instancia del repositorio
    repository = SQLReservationRepository(mock_session)

    # Crear una reserva de prueba
    reservation = Reservation(
        id=str(uuid4()),
        person_name=PersonName(first_name="John", last_name="Doe"),
        dni=DNI("12345678A"),
        phone_number=PhoneNumber(phone_number="+12345678901"),
        dates_check_io=DatesIO(
            check_in=datetime.now(),
            check_out=datetime.now() + timedelta(days=1),
        ),
    )

    # Ejecutar el método save y capturar la excepción
    with pytest.raises(Exception, match="Database error"):
        await repository.save(reservation)

    # Verificar que se llamó a rollback
    mock_session.rollback.assert_awaited_once()
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
