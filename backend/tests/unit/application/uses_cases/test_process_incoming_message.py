from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from backend.application.dtos.whatsapp_incoming_message import WhatsappIncomingMessage
from backend.application.use_cases.process_incoming_message import ProcessIncomingMessageUseCase
from backend.domain.repositories.message_repository import MessageRepository

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.unit,
]


async def test_execute_valid_message():
    # Mock dependencies
    message_repository = AsyncMock(spec=MessageRepository)

    # Crear instancia del caso de uso
    use_case = ProcessIncomingMessageUseCase(message_repository)

    # Simular un mensaje válido en la cola
    valid_input_message = WhatsappIncomingMessage(
        message_id="wamid.TEST",
        from_phone="34600000000",
        timestamp=str(int(datetime.now().timestamp())),
        content="Hello!",
    )

    # Ejecutar el caso de uso
    result = await use_case.execute(valid_input_message)

    # Verificar que el mensaje fue procesado y guardado
    assert result is not None
    assert result.is_valid is True
    message_repository.save.assert_awaited_once_with(result)


async def test_execute_invalid_message():
    # Mock dependencies
    message_repository = AsyncMock(spec=MessageRepository)

    # Crear instancia del caso de uso
    use_case = ProcessIncomingMessageUseCase(message_repository)

    # Simular un mensaje inválido en la cola
    invalid_input_message = WhatsappIncomingMessage(
        message_id="wamid.TEST",
        from_phone="34600000000",
        timestamp=str(int(datetime.now().timestamp())),
        content="",
    )

    # Ejecutar el caso de uso
    result = await use_case.execute(invalid_input_message)

    # Verificar que el mensaje no fue procesado ni guardado
    assert result is None
    message_repository.save.assert_not_awaited()
