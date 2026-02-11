"""
Recupera el mensaje más antiguo en la cola de mensajes entrantes y lo procesa.
"""

from datetime import datetime
from uuid import uuid4

from ...domain.entities.message import Message, Role
from ...domain.repositories.message_repository import MessageRepository
from ...domain.repositories.reservation_repository import ReservationRepository


class ProcessIncomingMessageUseCase:
    def __init__(
        self, message_repository: MessageRepository, reservation_repository: ReservationRepository
    ):
        self.message_repository = message_repository
        self.reservation_repository = reservation_repository

    def execute(self) -> Message | None:
        try:
            # Recuperar el mensaje más antiguo en la cola
            # message = self.message_queue.get_nowait()
            message = None  # Simulación de recuperación de mensaje

        except Exception:
            # Manejar el caso en que no hay mensajes en la cola
            return None

        # Procesar el mensaje recuperado

        # 1. Construir mensaje
        if message:
            message_processed = Message(
                id=str(uuid4()),
                timestamp=datetime.now(),
                role=Role.USER,
                content=message.content,
            )
            if not message_processed.is_valid():
                return None

            # 2. Guardar en BBDD
            self.message_repository.save(message_processed)

            return message_processed

        return None
