"""
Connection to database repository.
"""

from abc import ABC, abstractmethod

class DataBaseConnection(ABC):
    @abstractmethod
    def connect(self):
        """Establish a connection to the database."""
        pass

    @abstractmethod
    def disconnect(self):
        """Close the connection to the database."""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: dict = None):
        """Execute a query against the database."""
        pass