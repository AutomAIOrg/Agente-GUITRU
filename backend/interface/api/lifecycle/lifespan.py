from contextlib import asynccontextmanager

from fastapi import FastAPI

from ...dependencies import get_process_incoming_message_uc, get_queue_adapter
from ..lifecycle.orchestrator import Orchestrator


@asynccontextmanager
async def lifespan(app: FastAPI):
    queue = get_queue_adapter()
    process_incoming_message_uc = get_process_incoming_message_uc()

    orchestrator = Orchestrator(
        queue=queue,
        process_incoming_message_uc=process_incoming_message_uc,
    )
    app.state.orchestrator = orchestrator

    await orchestrator.start()
    try:
        yield
    finally:
        await orchestrator.stop()
