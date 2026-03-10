import asyncio
from unittest.mock import AsyncMock

import pytest

from backend.application.dtos.whatsapp_incoming_message import WhatsappIncomingMessage
from backend.interface.api.lifecycle.orchestrator import Orchestrator

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.unit,
]


class TestOrchestrator:
    @staticmethod
    def _build_message() -> WhatsappIncomingMessage:
        return WhatsappIncomingMessage(
            message_id="wamid.TEST",
            from_phone="34600000000",
            timestamp=1710000000,
            content="Hola",
        )

    async def test_start_creates_consumer_task_only_once(self):
        queue = AsyncMock()
        use_case = AsyncMock()

        orchestrator = Orchestrator(
            queue=queue,
            process_incoming_message_uc=use_case,
        )

        await orchestrator.start()
        first_task = orchestrator._task_queue_consumer

        await orchestrator.start()
        second_task = orchestrator._task_queue_consumer

        # Comprobar que no se crean dos consumers en paralelo
        assert first_task is not None
        assert first_task is second_task

        await orchestrator.stop()

    async def test_stop_cancels_and_clears_consumer_task(self):
        queue = AsyncMock()
        use_case = AsyncMock()

        orchestrator = Orchestrator(
            queue=queue,
            process_incoming_message_uc=use_case,
        )

        await orchestrator.start()
        assert orchestrator._task_queue_consumer is not None

        # Comprobar que el orquestador vuelve a quedar limpio tras parar la ejecución
        await orchestrator.stop()
        assert orchestrator._task_queue_consumer is None

    async def test_run_queue_consumer_gets_message_and_delegates_to_use_case(self):
        message = self._build_message()

        queue = AsyncMock()
        queue.get = AsyncMock(side_effect=[message, asyncio.CancelledError()])

        use_case = AsyncMock()

        orchestrator = Orchestrator(
            queue=queue,
            process_incoming_message_uc=use_case,
        )

        with pytest.raises(asyncio.CancelledError):
            await orchestrator._run_queue_consumer()

        queue.get.assert_awaited()
        use_case.execute.assert_awaited_once_with(message)

    async def test_run_queue_consumer_logs_and_continues_on_generic_exception(self):
        message = self._build_message()

        queue = AsyncMock()
        queue.get = AsyncMock(side_effect=[message, asyncio.CancelledError()])

        use_case = AsyncMock()
        use_case.execute = AsyncMock(side_effect=[RuntimeError("boom")])

        orchestrator = Orchestrator(
            queue=queue,
            process_incoming_message_uc=use_case,
        )

        with pytest.raises(asyncio.CancelledError):
            await orchestrator._run_queue_consumer()

        # Comprobar que el proceso loggea y sigue tras haber encontrado un error en el orquestador
        queue.get.assert_awaited()
        use_case.execute.assert_awaited_once_with(message)
