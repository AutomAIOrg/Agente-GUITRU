from dataclasses import dataclass

from ..value_objects.dates_io import DatesIO
from ..value_objects.dni import DNI
from ..value_objects.person_name import PersonName
from ..value_objects.phone_number import PhoneNumber


@dataclass
class Reservation:
    """Reserva de apartamento del cliente"""

    id: str
    person_name: PersonName
    dni: DNI
    phone_number: PhoneNumber
    dates_check_io: DatesIO
