from unittest.mock import AsyncMock

import pytest

from backend.infrastructure.persistence.sql_message_repository import SQLMessageRepository
from backend.infrastructure.persistence.sql_reservation_repository import SQLReservationRepository
from backend.infrastructure.persistence.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.unit,
]


async def test_uow_enter_initializes_repositories_and_commit_delegates():
    session = AsyncMock()
    db = AsyncMock()
    db.get_session.return_value = session

    async with SQLAlchemyUnitOfWork(db=db) as uow:
        assert isinstance(uow.messages, SQLMessageRepository)
        assert isinstance(uow.reservations, SQLReservationRepository)

        await uow.commit()

    db.get_session.assert_awaited_once()
    session.commit.assert_awaited_once()
    session.rollback.assert_not_awaited()
    session.close.assert_awaited_once()


async def test_uow_exit_rolls_back_on_exception_and_closes_session():
    session = AsyncMock()
    db = AsyncMock()
    db.get_session.return_value = session

    with pytest.raises(RuntimeError, match="boom"):
        async with SQLAlchemyUnitOfWork(db=db):
            raise RuntimeError("boom")

    db.get_session.assert_awaited_once()
    session.rollback.assert_awaited_once()
    session.close.assert_awaited_once()
