from datetime import datetime, timedelta

import pytest

from backend.domain.entities.message import Message, Role
from backend.domain.entities.reservation import Reservation
from backend.domain.value_objects.dates_io import DatesIO
from backend.domain.value_objects.dni import DNI
from backend.domain.value_objects.person_name import PersonName
from backend.domain.value_objects.phone_number import PhoneNumber

pytestmark = [
    pytest.mark.unit,
]


def test_message_is_valid():
    message = Message(
        id="1",
        user_id="user123",
        provider_message_id="wamid.TEST",
        timestamp=datetime.now(),
        role=Role.USER,
        content="Hello",
    )
    assert message.is_valid is True


def test_message_invalid_content():
    message = Message(
        id="1",
        user_id="user123",
        provider_message_id="wamid.TEST",
        timestamp=datetime.now(),
        role=Role.USER,
        content="",
    )
    assert message.is_valid is False


def test_reservation_initialization():
    person_name = PersonName(first_name="John", last_name="Doe")
    dni = DNI(dni="12345678A")
    phone_number = PhoneNumber(phone_number="+123456789")
    dates_io = DatesIO(check_in=datetime.now(), check_out=datetime.now() + timedelta(days=1))

    reservation = Reservation(
        id="1", person_name=person_name, dni=dni, phone_number=phone_number, dates_check_io=dates_io
    )

    assert reservation.person_name.first_name == "John"
    assert reservation.dni.dni == "12345678A"
    assert reservation.phone_number.phone_number == "+123456789"
    assert reservation.dates_check_io.is_valid is True
