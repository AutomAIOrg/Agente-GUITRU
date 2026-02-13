"""Adaptador de logging que implementa LoggerPort usando logging estándar."""

import json
import logging
from logging import Logger
from typing import Any

from ...application.logging.logger_port import LoggerPort


def _json_formatter(record: logging.LogRecord) -> str:
    # Formateador sencillo en JSON; se puede sustituir por libs más ricas (structlog).
    payload: dict[str, Any] = {
        "level": record.levelname,
        "logger": record.name,
        "message": record.getMessage(),
        "time": record.created,
    }

    # Mezcla el contexto si existe.
    extra = getattr(record, "context", None)
    if isinstance(extra, dict):
        payload.update(extra)
    return json.dumps(payload, ensure_ascii=False)


class StandardLoggerAdapter(LoggerPort):
    """Adapter concreto sobre logging estándar con formato JSON."""

    def __init__(self, logger: Logger):
        self._logger = logger

    def debug(self, message: str, context: dict[str, Any] | None = None) -> None:
        self._logger.debug(message, extra={"context": context or {}})

    def info(self, message: str, context: dict[str, Any] | None = None) -> None:
        self._logger.info(message, extra={"context": context or {}})

    def warn(self, message: str, context: dict[str, Any] | None = None) -> None:
        self._logger.warning(message, extra={"context": context or {}})

    def error(self, message: str, context: dict[str, Any] | None = None) -> None:
        self._logger.error(message, extra={"context": context or {}})

    def exception(self, message: str, context: dict[str, Any] | None = None) -> None:
        # Usa logging.exception para incluir stacktrace.
        self._logger.exception(message, extra={"context": context or {}})


def configure_logger(name: str = "app", level: int = logging.INFO) -> StandardLoggerAdapter:
    """Crea y configura un logger estándar con salida JSON a consola/stdout."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(fmt="%(message)s"))

        # Wrap para emitir JSON usando nuestro formateador.
        class _JsonFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
                return _json_formatter(record)

        handler.setFormatter(_JsonFormatter())
        logger.addHandler(handler)

    # Evita propagar a root si no se desea duplicar salida.
    logger.propagate = False
    return StandardLoggerAdapter(logger)