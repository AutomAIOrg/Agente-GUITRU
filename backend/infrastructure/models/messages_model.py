'''
Modelo de SQLAlchemy para mensajes.
'''

from datetime import datetime
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy.types import Enum

from .base_model import BaseModel


class MessagesModel (BaseModel):
    __tablename__ = 'messages'

    user_id: Mapped[str] = MappedColumn(String(255), nullable=False)
    timestamp: Mapped[datetime] = MappedColumn(DateTime, nullable=False)
    role: Mapped[str] = MappedColumn(String(50), nullable=False)
    content: Mapped[str] = MappedColumn(Text, nullable=False)