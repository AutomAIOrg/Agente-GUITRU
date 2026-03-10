"""
Implementación de repositorio SQL para manejar los mensajes en la base de datos.
"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.message import Message
from ...domain.repositories.message_repository import MessageRepository
from ..models.messages_model import MessagesModel


class SQLMessageRepository(MessageRepository):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def save_if_new(self, message: Message) -> bool:
        """
        Guardar un mensaje en la base de datos.
        Devuelve True si el mensaje se insertó.
        Devuelve False si el mensaje ya existía (asegura idempotencia).
        """
        # Lógica para guardar el mensaje en la base de datos SQL
        db_message = MessagesModel(
            id=message.id,
            user_id=message.user_id,
            provider_message_id=message.provider_message_id,
            timestamp=message.timestamp,
            role=message.role.value,
            content=message.content,
        )

        try:
            async with self.db_session.begin_nested():
                self.db_session.add(db_message)
                await self.db_session.flush()
                return True

        except IntegrityError:
            # Se comprueba si el mensaje ya existía para ignorar el error
            if await self.exists_message(message.provider_message_id):
                return False
            raise

    async def exists_message(self, provider_message_id: str) -> bool:
        """
        Comprueba si existe el mensaje en base de datos.
        """
        stmt = (
            select(MessagesModel.id)
            .where(MessagesModel.provider_message_id == provider_message_id)
            .limit(1)
        )
        result = await self.db_session.execute(stmt)
        return result.first() is not None
