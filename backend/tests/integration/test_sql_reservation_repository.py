"""
Tests de integración para SQLReservationRepository.

Suite mínima y sin redundancias que cubre:
- Conexión y schema de BD
- Persistencia del método save()
- Constraints (PK, NOT NULL)
- Transacciones (rollback)
- Volumen (batch de 30)
"""

from contextlib import suppress
from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from ...domain.value_objects.dates_io import DatesIO
from ...domain.value_objects.dni import DNI
from ...domain.value_objects.person_name import PersonName
from ...domain.value_objects.phone_number import PhoneNumber
from ...infrastructure.models.reservation_model import ReservationModel
from ...infrastructure.persistence.sql_reservation_repository import SQLReservationRepository
from ..fixtures.factories import ReservationFactory

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.integration,
    pytest.mark.repository,
    pytest.mark.database,
]


class TestConnectionAndSchema:
    """Verifica que la BD responde y el schema de reservas es correcto."""

    async def test_connection_and_table_schema(self, test_engine):
        async with test_engine.connect() as conn:
            assert (await conn.execute(text("SELECT 1"))).scalar() == 1

            columns = (await conn.execute(text("DESCRIBE reservations"))).fetchall()
            column_names = [c[0] for c in columns]

            for expected in (
                "id",
                "person_name",
                "dni",
                "phone_number",
                "dates_check_in",
                "dates_check_out",
                "created_at",
            ):
                assert expected in column_names, f"Falta columna '{expected}'"


class TestSave:
    """Verifica que save() persiste correctamente todos los campos."""

    async def test_save_persists_all_fields(self, clean_db_session):
        repo = SQLReservationRepository(clean_db_session)
        reservation_id = uuid4().hex
        reservation = ReservationFactory.create(
            id=reservation_id,
            person_name=PersonName(first_name="Ana", last_name="Pérez"),
            dni=DNI(dni="12345678Z"),
            phone_number=PhoneNumber(phone_number="+34600111222"),
            dates_check_io=DatesIO(
                check_in=datetime(2026, 3, 10, 15, 0, 0),
                check_out=datetime(2026, 3, 14, 12, 0, 0),
            ),
        )

        await repo.save(reservation)

        result = await clean_db_session.execute(
            select(ReservationModel).where(ReservationModel.id == reservation_id)
        )
        row = result.scalar_one()

        assert row.person_name == "Pérez, Ana"
        assert row.dni == "12345678Z"
        assert row.phone_number == "+34600111222"
        assert row.dates_check_in == datetime(2026, 3, 10, 15, 0, 0)
        assert row.dates_check_out == datetime(2026, 3, 14, 12, 0, 0)


class TestConstraints:
    """Verifica que la BD rechaza datos inválidos."""

    async def test_duplicate_id_raises_integrity_error(self, clean_db_session):
        repo = SQLReservationRepository(clean_db_session)
        duplicate_id = uuid4().hex
        reservation = ReservationFactory.create(id=duplicate_id)
        await repo.save(reservation)

        with pytest.raises(IntegrityError, match=r"Duplicate entry|UNIQUE"):
            await repo.save(ReservationFactory.create(id=duplicate_id))

    async def test_null_required_field_raises_error(self, clean_db_session):
        invalid = ReservationModel(
            id="null-reservation-test",
            person_name=None,
            dni="12345678Z",
            phone_number="+34600111222",
            dates_check_in=datetime(2026, 3, 10, 15, 0, 0),
            dates_check_out=datetime(2026, 3, 14, 12, 0, 0),
        )
        clean_db_session.add(invalid)

        with pytest.raises(IntegrityError, match=r"cannot be null|NOT NULL"):
            await clean_db_session.commit()

        await clean_db_session.rollback()


class TestTransactions:
    """Verifica que rollback funciona y no corrompe datos previos."""

    async def test_rollback_discards_and_preserves_prior_data(self, clean_db_session):
        repo = SQLReservationRepository(clean_db_session)

        rollback_id = uuid4().hex
        original = ReservationFactory.create(id=rollback_id)
        await repo.save(original)

        with suppress(Exception):
            await repo.save(ReservationFactory.create(id=rollback_id))

        result = await clean_db_session.execute(
            select(ReservationModel).where(ReservationModel.id == rollback_id)
        )
        assert result.scalar_one_or_none() is not None


class TestVolume:
    """Verifica persistencia básica con volumen moderado."""

    async def test_batch_30_reservations(self, clean_db_session):
        repo = SQLReservationRepository(clean_db_session)
        reservations = ReservationFactory.create_batch(count=30)
        batch_ids: list[str] = []

        for reservation in reservations:
            batch_ids.append(reservation.id)
            await repo.save(reservation)

        result = await clean_db_session.execute(
            select(ReservationModel).where(ReservationModel.id.in_(batch_ids))
        )
        assert len(result.scalars().all()) == 30
