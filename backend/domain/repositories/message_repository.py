"""
Repositorio para manejar los mensajes en la base de datos.
"""

from abc import ABC, abstractmethod

from ...domain.entities.message import Message


class MessageRepository(ABC):
    @abstractmethod
    async def save_if_new(self, message: Message) -> bool:
        """
        Guardar un mensaje en la base de datos.
        Devuelve True si el mensaje se insertó.
        Devuelve False si el mensaje ya existía (asegura idempotencia).
        """
        pass

    @abstractmethod
    async def exists_message(self, provider_message_id: str) -> bool:
        """
        Comprueba si existe el mensaje en base de datos.
        """
        pass
