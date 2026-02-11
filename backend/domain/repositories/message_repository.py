"""
Repositorio para manejar los mensajes en la base de datos.
"""

from abc import ABC, abstractmethod

from ...domain.entities.message import Message


class MessageRepository(ABC):
    @abstractmethod
    def save(self, message: Message) -> None:
        """
        Guardar un mensaje en la base de datos.
        """
        pass
