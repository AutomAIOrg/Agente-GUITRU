import hashlib
import hmac
import logging
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from ....application.dtos.whatsapp_incoming_message import WhatsappIncomingMessage
from ....application.interfaces.message_queue import MessageQueuePort
from ....infrastructure.config.whatsapp_settings import WhatsappSettings, get_whatsapp_settings
from ....interface.dependencies import get_queue_adapter

logger = logging.getLogger("whatsapp.webhook")
router = APIRouter(prefix="", tags=["chat"])


# Health check
@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/webhooks/whatsapp")
async def verify_whatsapp_webhook(
    settings: Annotated[WhatsappSettings, Depends(get_whatsapp_settings)],
    mode: Annotated[str | None, Query(alias="hub.mode")] = None,
    token: Annotated[str | None, Query(alias="hub.verify_token")] = None,
    challenge: Annotated[str | None, Query(alias="hub.challenge")] = None,
):
    """
    Llamada de Meta para verificar endpoint.
    Se debe devolver el challenge si el verify_token coincide.
    """
    if mode == "subscribe" and token == settings.VERIFY_TOKEN:
        return Response(content=challenge or "", media_type="text/plain")
    raise HTTPException(status_code=403, detail="Webhook verification failed")


@router.post("/webhooks/whatsapp")
async def receive_whatsapp_webhook(
    request: Request,
    settings: Annotated[WhatsappSettings, Depends(get_whatsapp_settings)],
    queue: Annotated[MessageQueuePort, Depends(get_queue_adapter)],
):
    """
    Recibe eventos WhatsApp:
    - messages (entrantes)
    - statuses (estados)
    """
    raw_body = await request.body()

    # 1. Validar firma
    signature = request.headers.get("X-Hub-Signature-256")
    app_secret = settings.META_APP_SECRET.get_secret_value()

    if not _verify_signature(app_secret, raw_body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # 2. Parsear payload
    payload = await request.json()

    # 3. Extraer mensajes tipo texto y añadirlos a la cola
    text_messages = _extract_text_messages(payload)
    for msg in text_messages:
        dto = WhatsappIncomingMessage(
            message_id=cast(str, msg.get("id")),
            from_phone=cast(str, msg.get("from")),
            timestamp=int(cast(str, msg.get("timestamp"))),
            content=(msg.get("text") or {}).get("body", ""),
        )

        await queue.put(dto)

    # 4. Responder 200 OK
    return {"status": "ok"}


def _verify_signature(app_secret: str, raw_body: bytes, signature_header: str | None) -> bool:
    """
    Verifica firma X-Hub-Signature-256 con el hash HMAC-SHA256 del payload (App Secret).
    """
    if not signature_header:
        return False
    if not signature_header.startswith("sha256="):
        return False

    received = signature_header.split("sha256=", 1)[1].strip()
    expected = hmac.new(app_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, received)


def _extract_text_messages(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Extrae mensajes entrantes tipo 'text' del payload.
    Esquema típico: entry -> changes -> value -> messages[].
    """
    out: list[dict[str, Any]] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for msg in value.get("messages", []):
                if msg.get("type") == "text":
                    out.append(msg)
    return out
