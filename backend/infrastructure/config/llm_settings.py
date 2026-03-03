from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """Lee config desde variables de entorno."""

    API_KEY: str = Field(default=..., description="API Key del proveedor de LLM")
    MODEL: str = Field(default=..., description="Modelo del proveedor de LLM")
    TIMEOUT_SECONDS: int = Field(default=..., description="Timeout para la llamada a la API")

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
