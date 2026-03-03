from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    """Settings del agente leídos desde variables de entorno."""

    MAX_ITERATIONS: int = Field(default=..., description="Máximo número de iteraciones")
    MAX_STEPS: int = Field(default=..., description="Máximo número de pasos en el plan")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AGENT_",
        extra="ignore",
    )


@lru_cache
def get_agent_settings() -> AgentSettings:
    """
    Devuelve una instancia cacheada de AgentSettings.
    Evita releer y parsear .env en cada request.
    """
    return AgentSettings()
