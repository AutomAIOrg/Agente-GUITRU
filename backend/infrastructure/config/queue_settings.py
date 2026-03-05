from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class QueueSettings(BaseSettings):
    """Settings de la cola de mensajes desde variables de entorno."""

    MAX_SIZE: int = Field(default=100, ge=1, description="Máximo número de items en cola")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="QUEUE_",
        extra="ignore",
    )


@lru_cache
def get_queue_settings() -> QueueSettings:
    """
    Devuelve una instancia cacheada de AgentSettings.
    Evita releer y parsear .env en cada request.
    """
    return QueueSettings()
