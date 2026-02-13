"""Contrato de logging para capas internas (Clean Architecture)."""

from abc import ABC, abstractmethod
from typing import Any


class LoggerPort(ABC):
    """Interfaz mínima para registrar eventos con contexto estructurado."""

    @abstractmethod
    def debug(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log para diagnóstico detallado (entornos de desarrollo)."""

    @abstractmethod
    def info(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log para hitos de flujo y eventos de negocio esperados."""

    @abstractmethod
    def warn(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log para situaciones anómalas recuperables."""

    @abstractmethod
    def error(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log para fallos de negocio no fatales o dependencias externas."""

    @abstractmethod
    def exception(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log de error con stacktrace para excepciones no controladas."""