from dataclasses import dataclass
from queue import Empty


@dataclass
class PersonName:
    """Nombre y apellidos del cliente"""

    FirstName: str
    LastName: str

    @property
    def is_valid(self) -> bool:
        return self.FirstName is not Empty and self.LastName is not Empty
