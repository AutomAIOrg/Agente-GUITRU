from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.repositories.message_repository import MessageRepository
from ..aplication.uses_cases.process_incoming_message import ProcessIncomingMessageUseCase
from ...infrastructure.persistence.sql_repository import SQLRepository


# Repositories
def get_message_repository(
    db_session: Annotated[AsyncSession, Depends(get_db_session)]
) -> MessageRepository:
    return SQLRepository(db_session=db_session)

def get_reservation_repository(
    db_session: Annotated[AsyncSession, Depends(get_db_session)]
) -> ReservationRepository:
    return SQLRepository(db_session=db_session)

# Use Cases
def get_process_incoming_message_uc(
    message_repository: Annotated[MessageRepository, Depends(get_message_repository)], 
    reservation_repository: Annotated[ReservationRepository, Depends(get_reservation_repository)]
) -> ProcessIncomingMessageUseCase:
    return ProcessIncomingMessageUseCase(
        message_repository=message_repository,
        reservation_repository=reservation_repository
    )
