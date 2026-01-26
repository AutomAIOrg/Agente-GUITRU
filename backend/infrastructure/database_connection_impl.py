"""
Implementation of database connection.
"""

import mysql.connector
from backend.domain.repoditory.database_connection import DataBaseConnection

class MySQLConnection(DataBaseConnection):
    @dataclass
    class DatesIO:
        """Check In and Check Out Dates"""

        CheckIn: datetime
        CheckOut: datetime

        @property
        def is_valid(self) -> bool:
            return self.CheckIn <= self.CheckOut