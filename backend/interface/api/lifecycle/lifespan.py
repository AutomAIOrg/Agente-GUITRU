from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.dependencies import get_db_adapter

from ...dependencies import get_queue_adapter
from ..lifecycle.orchestrator import Orchestrator


@asynccontextmanager
async def lifespan(app: FastAPI):
    queue = get_queue_adapter()
    db = get_db_adapter()

    orchestrator = Orchestrator(queue=queue, db=db)
    app.state.orchestrator = orchestrator

    await orchestrator.start()
    try:
        yield
    finally:
        await orchestrator.stop()
