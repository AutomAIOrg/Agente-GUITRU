from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession


class DatabaseAdapter(ABC):
    """Abstract base class for database adapters."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish a connection to the database."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the connection to the database."""
        pass

    @abstractmethod
    async def get_session(self) -> AsyncSession:
        """Get a database session."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check the health of the database connection."""
        pass
