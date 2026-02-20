from dataclasses import dataclass


@dataclass
class PersonName:
    """Nombre y apellidos del cliente"""

    first_name: str
    last_name: str

    @property
    def is_valid(self) -> bool:
        return bool(self.first_name.strip()) and bool(self.last_name.strip())
