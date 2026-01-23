import re
from dataclasses import dataclass


@dataclass
class PhoneNumber:
    """Número de teléfono del cliente"""

    phone_number: str

    @property
    def is_valid(self) -> bool:
        pattern = r"\b\+?\d(?:[\s.-]?\d){6,14}\b"
        return re.match(pattern, self.phone_number) is not None
