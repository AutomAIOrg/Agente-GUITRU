from asyncio import Queue
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.uses_cases.process_incoming_message import ProcessIncomingMessageUseCase
from ..dependencies import get_db_session
from ..domain.repositories.message_repository import MessageRepository
from ..domain.repositories.reservation_repository import ReservationRepository
from ..infrastructure.persistence.sql_message_repository import SQLMessageRepository
from ..infrastructure.persistence.sql_reservation_repository import SQLReservationRepository


# Repositories
def get_message_repository(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MessageRepository:
    return SQLMessageRepository(db_session=db_session)


def get_reservation_repository(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ReservationRepository:
    return SQLReservationRepository(db_session=db_session)


# Use Cases
def get_process_incoming_message_uc(
    message_repository: Annotated[MessageRepository, Depends(get_message_repository)],
    message_queue: Annotated[Queue, Depends(lambda: Queue())],
) -> ProcessIncomingMessageUseCase:
    return ProcessIncomingMessageUseCase(
        message_repository=message_repository,
        message_queue=message_queue,
    )
