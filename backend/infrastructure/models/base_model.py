"""
BaseModel para SQLAlchemy.
"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, MappedColumn

from ..models.base import Base


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[str] = MappedColumn(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at: Mapped[datetime] = MappedColumn(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = MappedColumn(
        DateTime(timezone=True), default=None, nullable=True, onupdate=lambda: datetime.now(UTC)
    )
