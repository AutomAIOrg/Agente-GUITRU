from asyncio import Queue

from ....application.dtos.whatsapp_incoming_message import WhatsappIncomingMessage
from ....application.interfaces.message_queue import MessageQueuePort


class AsyncioQueueAdapter(MessageQueuePort):
    def __init__(self, max_size: int = 100):
        self._queue: Queue[WhatsappIncomingMessage] = Queue(maxsize=max_size)

    async def put(self, msg: WhatsappIncomingMessage) -> None:
        """Incluye un nuevo mensaje a la cola."""
        await self._queue.put(msg)

    async def get(self) -> WhatsappIncomingMessage:
        """Extrae el mensaje más antiguo de la cola."""
        return await self._queue.get()
