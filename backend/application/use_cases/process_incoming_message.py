"""
Procesa un mensaje entrante de WhatsApp, lo transforma en una entidad de dominio
y lo persiste de forma idempotente.
"""

from collections.abc import Callable
from datetime import UTC, datetime
from uuid import uuid4

from ...domain.entities.message import Message, Role
from ..dtos.whatsapp_incoming_message import WhatsappIncomingMessage
from ..interfaces.unit_of_work import UnitOfWork


class ProcessIncomingMessageUseCase:
    def __init__(self, uow_factory: Callable[[], UnitOfWork]):
        self._uow_factory = uow_factory

    async def execute(self, message: WhatsappIncomingMessage) -> Message | None:
        # 1. Construir mensaje
        message_processed = Message(
            id=str(uuid4()),
            user_id=message.from_phone,
            provider_message_id=message.message_id,
            timestamp=datetime.fromtimestamp(message.timestamp, tz=UTC),
            role=Role.USER,
            content=message.content,
        )
        if not message_processed.is_valid:
            return None

        # 2. Guardar en BD
        async with self._uow_factory() as uow:
            saved = await uow.messages.save_if_new(message_processed)
            if not saved:
                return None

            await uow.commit()
            return message_processed
