'''
BaseModel para SQLAlchemy.
'''

from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, MappedColumn

from ..models.base import Base


class BaseModel(Base):
    __abstract__ = True
    
    id: Mapped[str] = MappedColumn(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at: Mapped[datetime] = MappedColumn(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = MappedColumn(DateTime(timezone=True), default=None, nullable=True, onupdate=lambda: datetime.now(timezone.utc))

