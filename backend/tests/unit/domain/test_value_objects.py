from datetime import datetime, timedelta

import pytest

from backend.domain.value_objects.dates_io import DatesIO
from backend.domain.value_objects.dni import DNI
from backend.domain.value_objects.person_name import PersonName
from backend.domain.value_objects.phone_number import PhoneNumber

pytestmark = [
    pytest.mark.unit,
]


def test_dni_validation():
    valid_dni = DNI("12345678A")
    invalid_dni = DNI("1234")

    assert valid_dni.is_valid is True
    assert invalid_dni.is_valid is False


def test_person_name_validation():
    valid_name = PersonName(first_name="John", last_name="Doe")
    invalid_name = PersonName(first_name="", last_name="Doe")

    assert valid_name.is_valid is True
    assert invalid_name.is_valid is False


def test_phone_number_validation():
    valid_phone = PhoneNumber(phone_number="+34655001122")
    invalid_phone = PhoneNumber(phone_number="123")

    assert valid_phone.is_valid is True
    assert invalid_phone.is_valid is False


def test_dates_io_validation():
    valid_dates = DatesIO(check_in=datetime.now(), check_out=datetime.now() + timedelta(days=1))
    invalid_dates = DatesIO(check_in=datetime.now(), check_out=datetime.now() - timedelta(days=1))

    assert valid_dates.is_valid is True
    assert invalid_dates.is_valid is False
