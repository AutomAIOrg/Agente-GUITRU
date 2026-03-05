"""
Factories para generar datos de test de entidades de dominio.

Usa Faker para generar datos realistas y variados.
"""

from datetime import UTC, datetime
from uuid import uuid4

from faker import Faker

from ...domain.entities.message import Message, Role
from ...domain.entities.reservation import Reservation
from ...domain.value_objects.dates_io import DatesIO
from ...domain.value_objects.dni import DNI
from ...domain.value_objects.person_name import PersonName
from ...domain.value_objects.phone_number import PhoneNumber

fake = Faker(["es_ES", "es_MX"])  # Español para datos más realistas


class MessageFactory:
    """Factory para crear instancias de Message con datos de test."""

    @staticmethod
    def create(
        id: str | None = None,
        user_id: str | None = None,
        provider_message_id: str | None = None,
        timestamp: datetime | None = None,
        role: Role | None = None,
        content: str | None = None,
    ) -> Message:
        """
        Crea un mensaje con datos realistas.
        Permite sobrescribir cualquier campo para casos específicos.
        """
        return Message(
            id=id or str(uuid4()),
            user_id=user_id or str(uuid4()),
            provider_message_id=provider_message_id or None,
            timestamp=timestamp or datetime.now(UTC),
            role=role or Role.USER,
            content=fake.sentence(nb_words=10) if content is None else content,
        )

    @staticmethod
    def create_user_message(**kwargs) -> Message:
        """Crea un mensaje de usuario."""
        return MessageFactory.create(role=Role.USER, **kwargs)

    @staticmethod
    def create_assistant_message(**kwargs) -> Message:
        """Crea un mensaje de asistente."""
        return MessageFactory.create(role=Role.ASSISTANT, **kwargs)

    @staticmethod
    def create_batch(count: int = 5, **kwargs) -> list[Message]:
        """Crea múltiples mensajes."""
        return [MessageFactory.create(**kwargs) for _ in range(count)]


class ReservationFactory:
    """Factory para crear instancias de Reservation con datos de test."""

    @staticmethod
    def create(
        id: str | None = None,
        person_name: PersonName | None = None,
        dni: DNI | None = None,
        phone_number: PhoneNumber | None = None,
        dates_check_io: DatesIO | None = None,
    ) -> Reservation:
        """
        Crea una reserva con datos realistas.
        Permite sobrescribir cualquier campo para casos específicos.
        """
        return Reservation(
            id=id or str(uuid4()),
            person_name=person_name
            or PersonName(first_name=fake.first_name(), last_name=fake.last_name()),
            dni=dni or DNI(dni=fake.bothify(text="########?").upper()),
            phone_number=phone_number or PhoneNumber(phone_number=fake.phone_number()),
            dates_check_io=dates_check_io
            or DatesIO(
                check_in=datetime.combine(fake.future_date(end_date="+30d"), datetime.min.time()),
                check_out=datetime.combine(fake.future_date(end_date="+60d"), datetime.min.time()),
            ),
        )

    @staticmethod
    def create_batch(count: int = 5, **kwargs) -> list[Reservation]:
        """Crea múltiples reservas."""
        return [ReservationFactory.create(**kwargs) for _ in range(count)]
