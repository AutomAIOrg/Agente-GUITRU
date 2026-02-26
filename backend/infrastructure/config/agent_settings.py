from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    """Settings del agente leídos desde variables de entorno."""

    MAX_ITERATIONS: int = 2
    MAX_STEPS: int = 8

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
