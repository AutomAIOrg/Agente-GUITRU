"""
Implementación de repositorio SQL para manejar los mensajes en la base de datos.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.message import Message
from ...domain.repositories.message_repository import MessageRepository
from ...shared.logging.logging_config import get_logger
from ..models.messages_model import MessagesModel

logger = get_logger(__name__)


class SQLMessageRepository(MessageRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def save(self, message: Message) -> None:
        """
        Guardar un mensaje en la base de datos.
        """
        # Lógica para guardar el mensaje en la base de datos SQL
        logger.debug("Guardando mensaje: id=%s user_id=%s", message.id, message.user_id)

        db_message = MessagesModel(
            id=message.id,
            user_id=message.user_id,
            timestamp=message.timestamp,
            role=message.role.value,
            content=message.content,
        )

        self.db_session.add(db_message)

        try:
            await self.db_session.commit()
            logger.debug("Mensaje guardado: id=%s", message.id)

        except Exception:
            await self.db_session.rollback()
            logger.exception("Error al guardar mensaje id=%s", message.id)
            raise
