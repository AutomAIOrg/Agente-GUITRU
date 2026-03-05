"""
Recupera el mensaje más antiguo en la cola de mensajes entrantes y lo procesa.
"""

from asyncio import Queue
from datetime import datetime
from uuid import uuid4

from ...domain.entities.message import Message, Role
from ...domain.repositories.message_repository import MessageRepository
from ...shared.logging.logging_config import get_logger

logger = get_logger(__name__)


class ProcessIncomingMessageUseCase:
    def __init__(self, message_repository: MessageRepository, message_queue: Queue[Message]):
        self.message_repository = message_repository
        self.message_queue = message_queue

    async def execute(self) -> Message | None:
        try:
            # Recuperar el mensaje más antiguo en la cola
            message = await self.message_queue.get()
        except Exception as e:
            logger.warning("Error al obtener mensaje de la cola: %s", e)
            return None

        if not message:
            logger.debug("Mensaje vacío recibido, ignorando")
            return None

        if message:
            logger.debug(
                "Mensaje recibido: user_id=%s content='%.50s'",
                message.user_id,
                message.content
            )

            # Construcción del mensaje
            message_processed = Message(
                id=str(uuid4()),
                user_id=message.user_id,
                timestamp=datetime.now(),
                role=Role.USER,
                content=message.content,
            )

            if not message_processed.is_valid:
                logger.warning("Mensaje inválido descartado: user_id=%s", message.user_id)
                return None

            # Guardar el mensaje procesado en la base de datos
            await self.message_repository.save(message_processed)
            logger.info(
                "Mensaje procesado y guardado: id=%s user_id=%s",
                message_processed.id,
                message_processed.user_id
            )

            return message_processed
        return None
