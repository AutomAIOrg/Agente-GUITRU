"""
Recupera el mensaje más antiguo en la cola de mensajes entrantes y lo procesa.
"""

from asyncio import Queue
from datetime import datetime
from typing import Any
from uuid import uuid4

from ...domain.entities.message import Message, Role
from ...domain.repositories.message_repository import MessageRepository


class ProcessIncomingMessageUseCase:
    def __init__(self, message_repository: MessageRepository, message_queue: Queue[Any]):
        self.message_repository = message_repository
        self.message_queue = message_queue

    async def execute(self) -> Message | None:
        try:
            # Recuperar el mensaje más antiguo en la cola
            message = await self.message_queue.get()
        except Exception:
            # Manejar el caso en que no hay mensajes en la cola
            return None

        # Procesar el mensaje recuperado

        # 1. Construir mensaje
        if message:
            message_processed = Message(
                id=str(uuid4()),
                user_id=message.user_id,
                timestamp=datetime.now(),
                role=Role.USER,
                content=message.content,
            )
            if not message_processed.is_valid:
                return None

            # 2. Guardar en BBDD
            await self.message_repository.save(message_processed)

            return message_processed

        return None
