from abc import ABC, abstractmethod

from pydantic import BaseModel


class LLMPort(ABC):
    @abstractmethod
    def generate_plan(self, system: str, user: str, schema: type[BaseModel]) -> BaseModel:
        """Devuelve un objeto validado con Pydantic (schema)."""
        pass
