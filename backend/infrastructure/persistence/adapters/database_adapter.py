from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession


class DatabaseAdapter(ABC):
    """Abstract base class for database adapters."""

    @abstractmethod
    def connect(self) -> AsyncSession:
        """Establish a connection to the database."""
        pass

    @abstractmethod
    def disconnect(self) -> AsyncSession:
        """Close the connection to the database."""
        pass

    @abstractmethod
    def get_session(self) -> AsyncSession:
        """Get a database session."""
        pass

    @abstractmethod
    def health_check(self) -> AsyncSession:
        """Check the health of the database connection."""
        pass