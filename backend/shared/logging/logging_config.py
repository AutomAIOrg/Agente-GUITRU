import logging
import sys
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class LogSettings(BaseSettings):
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_log_settings() -> LogSettings:
    return LogSettings()


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


# Esta configuración de logging se puede llamar al inicio de la aplicación
# para configurar el logging globalmente.
def configure_logging() -> None:
    settings = get_log_settings()
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(levelname)s %(asctime)s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,
    )


# Eliminar esta línea cuando se tenga main o app.
configure_logging()
