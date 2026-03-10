from abc import ABC, abstractmethod

from ..dtos.whatsapp_incoming_message import WhatsappIncomingMessage


class MessageQueuePort(ABC):
    @abstractmethod
    async def put(self, msg: WhatsappIncomingMessage) -> None:
        """Incluye un nuevo mensaje a la cola."""
        pass

    @abstractmethod
    async def get(self) -> WhatsappIncomingMessage:
        """Extrae el mensaje más antiguo de la cola."""
        pass
