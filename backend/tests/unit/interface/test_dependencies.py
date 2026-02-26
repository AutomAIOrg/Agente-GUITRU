from asyncio import Queue
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.use_cases.process_incoming_message import ProcessIncomingMessageUseCase
from backend.domain.repositories.message_repository import MessageRepository
from backend.infrastructure.persistence.sql_message_repository import SQLMessageRepository
from backend.infrastructure.persistence.sql_reservation_repository import SQLReservationRepository
from backend.interface.dependencies import (
    get_message_repository,
    get_process_incoming_message_uc,
    get_reservation_repository,
)

pytestmark = [
    pytest.mark.unit,
]


def test_get_message_repository():
    # Mock AsyncSession
    mock_session = AsyncMock(spec=AsyncSession)

    # Llamar a la función
    repository = get_message_repository(mock_session)

    # Verificar que devuelve una instancia de SQLMessageRepository
    assert isinstance(repository, SQLMessageRepository)
    assert repository.db_session == mock_session


def test_get_reservation_repository():
    # Mock AsyncSession
    mock_session = AsyncMock(spec=AsyncSession)

    # Llamar a la función
    repository = get_reservation_repository(mock_session)

    # Verificar que devuelve una instancia de SQLReservationRepository
    assert isinstance(repository, SQLReservationRepository)
    assert repository.db_session == mock_session


def test_get_process_incoming_message_uc():
    # Mock dependencias
    mock_message_repository = AsyncMock(spec=MessageRepository)
    message_queue = AsyncMock(spec=Queue)

    # Llamar a la función
    use_case = get_process_incoming_message_uc(
        message_repository=mock_message_repository,
        message_queue=message_queue,
    )

    # Verificar que devuelve una instancia de ProcessIncomingMessageUseCase
    assert isinstance(use_case, ProcessIncomingMessageUseCase)
    assert use_case.message_repository == mock_message_repository
    assert use_case.message_queue == message_queue
