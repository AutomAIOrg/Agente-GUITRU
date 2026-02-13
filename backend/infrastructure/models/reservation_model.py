"""
Modelo de SQLAlchemy para mensajes.
"""

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, MappedColumn

from .base_model import BaseModel


class ReservationModel(BaseModel):
    __tablename__ = "reservations"

    person_name: Mapped[str] = MappedColumn(String, nullable=False)
    dni: Mapped[str] = MappedColumn(String, nullable=False)
    phone_number: Mapped[str] = MappedColumn(String, nullable=False)
    dates_check_in: Mapped[datetime] = MappedColumn(DateTime, nullable=False)
    dates_check_out: Mapped[datetime] = MappedColumn(DateTime, nullable=False)
