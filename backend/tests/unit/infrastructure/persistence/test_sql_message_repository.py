from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from backend.domain.entities.message import Message, Role
from backend.infrastructure.persistence.sql_message_repository import SQLMessageRepository

pytestmark = [
    pytest.mark.unit,
    pytest.mark.asyncio,
]

async def test_save_message():
    # Mock AsyncSession
    mock_session = AsyncMock()

    # Crear instancia del repositorio
    repository = SQLMessageRepository(mock_session)

    # Crear un mensaje de prueba
    message = Message(
        id=str(uuid4()),
        user_id="user123",
        timestamp=datetime.now(),
        role=Role.USER,
        content="Hello!",
    )

    # Ejecutar el método save
    await repository.save(message)

    # Verificar que se llamaron los métodos correctos
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()

async def test_save_message_rollback_on_error():
    # Mock AsyncSession
    mock_session = AsyncMock()
    mock_session.commit.side_effect = Exception("Database error")

    # Crear instancia del repositorio
    repository = SQLMessageRepository(mock_session)

    # Crear un mensaje de prueba
    message = Message(
        id=str(uuid4()),
        user_id="user123",
        timestamp=datetime.now(),
        role=Role.USER,
        content="Hello!",
    )

    # Ejecutar el método save y capturar la excepción
    with pytest.raises(Exception, match="Database error"):
        await repository.save(message)

    # Verificar que se llamó a rollback
    mock_session.rollback.assert_awaited_once()
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
