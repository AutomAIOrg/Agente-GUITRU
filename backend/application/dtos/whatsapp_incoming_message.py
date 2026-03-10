from dataclasses import dataclass


@dataclass(frozen=True)
class WhatsappIncomingMessage:
    message_id: str
    from_phone: str
    timestamp: int
    content: str
