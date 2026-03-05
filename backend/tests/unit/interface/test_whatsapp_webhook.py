import hashlib
import hmac
import json
from asyncio import Queue
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr

from backend.application.dtos.whatsapp_incoming_message import WhatsappIncomingMessage

pytestmark = [pytest.mark.unit]


class TestWhatsAppWebhook:
    """
    Tests unitarios de la capa Interface:
    - Verificación GET del webhook
    - Recepción POST con firma válida => encola
    - Recepción POST con firma inválida => 403 y no encola

    NOTA:
    Este test asume que tu router existe y usa Depends para:
      - settings (VERIFY_TOKEN, APP_SECRET)
      - message_queue (asyncio.Queue[Message])
    """

    def _build_app(
        self, *, queue: Queue, verify_token: str, app_secret: str
    ) -> tuple[FastAPI, TestClient]:
        """
        Construye una FastAPI mínima para testear el router del webhook.
        Inyecta overrides de dependencias para que:
          - NO leamos .env
          - usemos una cola controlada por el test
        """
        from backend.infrastructure.config.whatsapp_settings import get_whatsapp_settings
        from backend.interface.api.webhooks.whatsapp_webhook import router
        from backend.interface.dependencies import get_queue_adapter

        app = FastAPI()
        app.include_router(router)

        # Override settings: no dependemos de env vars
        app.dependency_overrides[get_whatsapp_settings] = lambda: SimpleNamespace(
            VERIFY_TOKEN=verify_token,
            META_APP_SECRET=SecretStr(app_secret),
        )

        # Override cola: usamos una instancia controlada por el test
        app.dependency_overrides[get_queue_adapter] = lambda: queue

        return TestClient(app)

    def _sign(self, raw_body: bytes, app_secret: str) -> str:
        digest = hmac.new(app_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
        return f"sha256={digest}"

    def test_verify_get_returns_challenge_when_token_matches(self):
        queue = Queue()
        verify_token = "test-verify-token"
        app_secret = "test-app-secret"
        client = self._build_app(queue=queue, verify_token=verify_token, app_secret=app_secret)

        resp = client.get(
            "/webhooks/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": verify_token,
                "hub.challenge": "12345",
            },
        )

        assert resp.status_code == 200
        assert resp.text == "12345"

    def test_post_with_invalid_signature_returns_403_and_does_not_enqueue(self):
        queue = Queue()
        verify_token = "test-verify-token"
        app_secret = "test-app-secret"
        client = self._build_app(queue=queue, verify_token=verify_token, app_secret=app_secret)

        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "waba-id",
                    "changes": [
                        {
                            "field": "messages",
                            "value": {
                                "messages": [
                                    {
                                        "from": "34600000000",
                                        "id": "wamid.TEST",
                                        "timestamp": "1710000000",
                                        "type": "text",
                                        "text": {"body": "Hola"},
                                    }
                                ]
                            },
                        }
                    ],
                }
            ],
        }
        raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

        resp = client.post(
            "/webhooks/whatsapp",
            data=raw,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": "sha256=WRONG_SIGNATURE",
            },
        )

        assert resp.status_code == 403
        assert queue.qsize() == 0

    def test_post_with_valid_signature_enqueues_message(self):
        queue = Queue()
        verify_token = "test-verify-token"
        app_secret = "test-app-secret"
        client = self._build_app(queue=queue, verify_token=verify_token, app_secret=app_secret)

        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "waba-id",
                    "changes": [
                        {
                            "field": "messages",
                            "value": {
                                "messages": [
                                    {
                                        "from": "34600000000",
                                        "id": "wamid.TEST",
                                        "timestamp": "1710000000",
                                        "type": "text",
                                        "text": {"body": "Hola desde test"},
                                    }
                                ]
                            },
                        }
                    ],
                }
            ],
        }
        raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        signature = self._sign(raw, app_secret)

        resp = client.post(
            "/webhooks/whatsapp",
            data=raw,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": signature,
            },
        )

        assert resp.status_code == 200
        assert queue.qsize() == 1

        msg = queue.get_nowait()
        assert isinstance(msg, WhatsappIncomingMessage)
        assert msg.from_phone == "34600000000"
        assert msg.content == "Hola desde test"
        assert msg.message_id == "wamid.TEST"
        assert msg.timestamp == "1710000000"
