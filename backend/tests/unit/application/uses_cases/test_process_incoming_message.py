from asyncio import Queue
from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.application.use_cases.process_incoming_message import ProcessIncomingMessageUseCase
from backend.domain.entities.message import Message, Role
from backend.domain.repositories.message_repository import MessageRepository

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.unit,
]


async def test_execute_no_message():
    # Mock dependencies
    message_repository = AsyncMock(spec=MessageRepository)
    message_queue = AsyncMock(spec=Queue)

    # Crear instancia del caso de uso
    use_case = ProcessIncomingMessageUseCase(message_repository, message_queue)

    # Simular que no hay mensajes en la cola
    message_queue.get.side_effect = Exception("No messages in queue")

    # Ejecutar el caso de uso
    result = await use_case.execute()

    # Verificar que el resultado es None
    assert result is None
    message_queue.get.assert_called_once()


async def test_execute_valid_message():
    # Mock dependencies
    message_repository = AsyncMock(spec=MessageRepository)
    message_queue = AsyncMock(spec=Queue)

    # Crear instancia del caso de uso
    use_case = ProcessIncomingMessageUseCase(message_repository, message_queue)

    # Simular un mensaje válido en la cola
    valid_message = Message(
        id=str(uuid4()),
        user_id="user123",
        timestamp=datetime.now(),
        role=Role.USER,
        content="Hello!",
    )
    message_queue.get.return_value = valid_message

    # Ejecutar el caso de uso
    result = await use_case.execute()

    # Verificar que el mensaje fue procesado y guardado
    assert result is not None
    assert result.is_valid is True
    message_repository.save.assert_awaited_once_with(result)
    message_queue.get.assert_called_once()


async def test_execute_invalid_message():
    # Mock dependencies
    message_repository = AsyncMock(spec=MessageRepository)
    message_queue = AsyncMock(spec=Queue)

    # Crear instancia del caso de uso
    use_case = ProcessIncomingMessageUseCase(message_repository, message_queue)

    # Simular un mensaje inválido en la cola
    invalid_message = Message(
        id=str(uuid4()),
        user_id="user123",
        timestamp=datetime.now(),
        role=Role.USER,
        content="",  # Contenido inválido
    )
    message_queue.get.return_value = invalid_message

    # Ejecutar el caso de uso
    result = await use_case.execute()

    # Verificar que el mensaje no fue procesado ni guardado
    assert result is None
    message_repository.save.assert_not_awaited()
    message_queue.get.assert_called_once()
