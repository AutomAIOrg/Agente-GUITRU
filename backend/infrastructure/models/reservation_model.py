"""
Modelo de SQLAlchemy para reservas.
"""

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, MappedColumn

from .base_model import BaseModel


class ReservationModel(BaseModel):
    __tablename__ = "reservations"

    person_name: Mapped[str] = MappedColumn(String(255), nullable=False)
    dni: Mapped[str] = MappedColumn(String(20), nullable=False)
    phone_number: Mapped[str] = MappedColumn(String(32), nullable=False)
    dates_check_in: Mapped[datetime] = MappedColumn(DateTime, nullable=False)
    dates_check_out: Mapped[datetime] = MappedColumn(DateTime, nullable=False)
