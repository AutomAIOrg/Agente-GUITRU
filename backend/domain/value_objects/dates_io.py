from dataclasses import dataclass
from datetime import datetime


@dataclass
class DatesIO:
    """Fechas de Check In y Check Out"""

    check_in: datetime
    check_out: datetime

    @property
    def is_valid(self) -> bool:
        return self.check_in <= self.check_out