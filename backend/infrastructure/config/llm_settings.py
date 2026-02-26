from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """Lee config desde variables de entorno."""

    API_KEY: str = ""
    MODEL: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LLM_OPENAI_",
        extra="ignore",
    )


@lru_cache
def get_llm_settings() -> LLMSettings:
    """
    Guarda en caché los settings.
    Evita recrear y parsear .env en cada request.
    """
    return LLMSettings()
