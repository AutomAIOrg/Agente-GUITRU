from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.interface.api.lifecycle.lifespan import lifespan


def test_lifespan_creates_starts_and_stops_orchestrator(monkeypatch):
    fake_queue = object()
    fake_use_case = object()

    started = False
    stopped = False

    class FakeOrchestrator:
        def __init__(self, queue, process_incoming_message_uc):
            self.queue = queue
            self.process_incoming_message_uc = process_incoming_message_uc

        async def start(self):
            nonlocal started
            started = True

        async def stop(self):
            nonlocal stopped
            stopped = True

    # Parcheamos exactamente los símbolos usados por lifespan.py
    monkeypatch.setattr(
        "backend.interface.api.lifecycle.lifespan.get_queue_adapter",
        lambda: fake_queue,
    )
    monkeypatch.setattr(
        "backend.interface.api.lifecycle.lifespan.get_process_incoming_message_uc",
        lambda: fake_use_case,
    )
    monkeypatch.setattr(
        "backend.interface.api.lifecycle.lifespan.Orchestrator",
        FakeOrchestrator,
    )

    app = FastAPI(lifespan=lifespan)

    @app.get("/health-test")
    async def health_test():
        return {"ok": True}

    with TestClient(app) as client:
        response = client.get("/health-test")
        assert response.status_code == 200

        assert started is True
        assert hasattr(client.app.state, "orchestrator")
        assert client.app.state.orchestrator.queue is fake_queue
        assert client.app.state.orchestrator.process_incoming_message_uc is fake_use_case

    assert stopped is True
