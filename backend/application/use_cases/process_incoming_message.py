"""
Recupera el mensaje más antiguo en la cola de mensajes entrantes y lo procesa.
"""

from datetime import datetime
from uuid import uuid4

from ...application.dtos.whatsapp_incoming_message import WhatsappIncomingMessage
from ...domain.entities.message import Message, Role
from ...domain.repositories.message_repository import MessageRepository


class ProcessIncomingMessageUseCase:
    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    async def execute(self, message: WhatsappIncomingMessage) -> Message | None:
        # 1. Construir mensaje
        message_processed = Message(
            id=str(uuid4()),
            user_id=message.from_phone,
            provider_message_id=message.message_id,
            timestamp=datetime.fromtimestamp(message.timestamp),
            role=Role.USER,
            content=message.content,
        )
        print(message_processed)
        if not message_processed.is_valid:
            return None

        # 2. Guardar en BBDD
        await self.message_repository.save(message_processed)

        print("saved")

        return message_processed
