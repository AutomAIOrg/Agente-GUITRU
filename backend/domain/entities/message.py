from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from queue import Empty


class Role(Enum):
    """Definición de roles para los mensajes"""

    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """Mensaje recibido/enviado agente"""

    id: str
    user_id: str
    timestamp: datetime
    role: Role
    content: str

    @property
    def is_valid(self) -> bool:
        return self.content is not Empty
