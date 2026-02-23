"""
Modelo de SQLAlchemy para mensajes.
"""

from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, MappedColumn

from .base_model import BaseModel


class MessagesModel(BaseModel):
    __tablename__ = "messages"

    user_id: Mapped[str] = MappedColumn(String(255), nullable=False)
    timestamp: Mapped[datetime] = MappedColumn(DateTime, nullable=False)
    role: Mapped[str] = MappedColumn(String(50), nullable=False)
    content: Mapped[str] = MappedColumn(Text, nullable=False)
