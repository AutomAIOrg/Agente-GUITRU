import asyncio
import logging
from contextlib import suppress

from ....application.dtos.whatsapp_incoming_message import WhatsappIncomingMessage
from ....application.interfaces.message_queue import MessageQueuePort
from ....application.use_cases.process_incoming_message import ProcessIncomingMessageUseCase
from ....domain.repositories.message_repository import MessageRepository
from ....infrastructure.persistence.adapters.base_sqlalchemy_adapter import DatabaseAdapter
from ....infrastructure.persistence.sql_message_repository import SQLMessageRepository

logger = logging.getLogger("orchestrator")


class Orchestrator:
    """Orquestador para gestionar el flujo del programa."""

    def __init__(self, queue: MessageQueuePort, db: DatabaseAdapter):
        self._queue = queue
        self._db = db
        self._task_queue_consumer: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        """Crea tareas para la ejecución del orquestador."""
        if self._task_queue_consumer is not None:
            return
        self._stop_event.clear()
        self._task_queue_consumer = asyncio.create_task(
            self._run_queue_consumer(), name="queue_consumer"
        )
        logger.info("Orquestador iniciado")

    async def stop(self) -> None:
        """Interrupción del orquestador."""
        if self._task_queue_consumer is None:
            return
        self._stop_event.set()
        self._task_queue_consumer.cancel()
        with suppress(asyncio.CancelledError):
            await self._task_queue_consumer

        self._task_queue_consumer = None
        logger.info("Orquestador parado")

    async def _run_queue_consumer(self) -> None:
        while not self._stop_event.is_set():
            message = await self._queue.get()
            await self._handle_message(message)

    async def _handle_message(self, msg: WhatsappIncomingMessage) -> None:
        session = await self._db.get_session()
        try:
            message_repository: MessageRepository = SQLMessageRepository(db_session=session)
            process_incoming_message_uc = ProcessIncomingMessageUseCase(
                message_repository=message_repository
            )
            await process_incoming_message_uc.execute(msg)
            await session.commit()
        except Exception:
            await session.rollback()
            logger.exception("Error procesando mensaje %s", getattr(msg, "message_id", None))
        finally:
            await session.close()
