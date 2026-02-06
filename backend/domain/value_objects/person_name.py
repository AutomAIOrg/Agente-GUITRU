from dataclasses import dataclass
from queue import Empty


@dataclass
class PersonName:
    """Nombre y apellidos del cliente"""

    first_name: str
    last_name: str

    @property
    def is_valid(self) -> bool:
        return self.first_name is not Empty and self.last_name is not Empty
