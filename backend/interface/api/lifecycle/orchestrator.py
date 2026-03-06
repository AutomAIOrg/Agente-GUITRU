import asyncio
import logging
from contextlib import suppress

from backend.application.interfaces.message_queue import MessageQueuePort
from backend.application.use_cases.process_incoming_message import ProcessIncomingMessageUseCase

logger = logging.getLogger("orchestrator")


class Orchestrator:
    """Orquestador para gestionar el flujo del programa."""

    def __init__(
        self, queue: MessageQueuePort, process_incoming_message_uc: ProcessIncomingMessageUseCase
    ):
        self._queue = queue
        self._process_incomming_message_uc = process_incoming_message_uc
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
            try:
                message = await self._queue.get()
                await self._process_incomming_message_uc.execute(message)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Error procesando item de la cola.")
