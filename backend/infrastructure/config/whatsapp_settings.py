from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class WhatsappSettings(BaseSettings):
    """Settings del agente leídos desde variables de entorno."""

    PHONE_NUMBER_ID: str = Field(default=..., description="ID del número de teléfono Cloud API")
    WABA_ID: str = Field(default=..., description="")
    ACCESS_TOKEN: SecretStr = Field(default=..., description="Token Cloud API (dev/prod)")
    VERIFY_TOKEN: str = Field(default=..., description="Verify token del webhook")
    META_APP_SECRET: SecretStr = Field(
        default=..., description="Meta App Secret (para validar X-Hub-Signature-256)"
    )
    META_GRAPH_VERSION: str = Field(default=..., description="Versión del Graph API")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="WA_",
        extra="ignore",
    )


@lru_cache
def get_whatsapp_settings() -> WhatsappSettings:
    """
    Devuelve una instancia cacheada de WhatsappSettings.
    Evita releer y parsear .env en cada request.
    """
    return WhatsappSettings()
