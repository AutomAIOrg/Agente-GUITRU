import re
from dataclasses import dataclass


@dataclass
class DNI:
    """Número de identificación fiscal (NIF) del cliente"""

    dni: str

    @property
    def is_valid(self) -> bool:
        pattern = r"(?i)\b\d{8}[A-Z]\b"
        match = re.match(pattern, self.dni)
        return match is not None
