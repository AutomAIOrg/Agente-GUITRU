"""
Implementación de repositorio SQL para manejar los mensajes en la base de datos.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.message import Message
from ...domain.repositories.message_repository import MessageRepository
from ..models.messages_model import MessagesModel


class SQLMessageRepository(MessageRepository):

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def save(self, message: Message) -> None:
        '''
        Guardar un mensaje en la base de datos.
        '''
        # Lógica para guardar el mensaje en la base de datos SQL
        db_message = MessagesModel(
            id=message.id,
            user_id=message.user_id,
            timestamp=message.timestamp,
            role=message.role.value,
            content=message.content
        )
        
        self.db_session.add(db_message)

        try:
            await self.db_session.commit()
            
        except Exception as e:
            await self.db_session.rollback()
            print(f"Error saving message: {e}")
            raise e
           