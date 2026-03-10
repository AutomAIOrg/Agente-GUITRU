from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Role(Enum):
    """Definición de roles para los mensajes"""

    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """Mensaje recibido/enviado agente"""

    id: str
    user_id: str
    provider_message_id: str
    timestamp: datetime
    role: Role
    content: str

    @property
    def is_valid(self) -> bool:
        return bool(self.content.strip())
