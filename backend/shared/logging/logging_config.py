import logging
import sys
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class LogSettings(BaseSettings):
    LOG_LEVEL: str = "DEBUG"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_log_settings() -> LogSettings:
    return LogSettings()


def configure_logging() -> None:
    settings = get_log_settings()
    logging.basicConfig(
        level=settings.LOG_LEVEL.upper(),
        format="%(levelname)s %(asctime)s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
