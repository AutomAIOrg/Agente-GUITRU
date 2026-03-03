from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CalendarSettings(BaseSettings):
    """Lee config desde variables de entorno."""

    CALENDAR_ID: str = Field(default=..., description="ID del calendario")
    TIMEZONE: str = Field(default=..., description="Huso horario")
    SEND_UPDATES: Literal["none", "all", "externalOnly"] = Field(
        default=..., description="Envío de notificación al modificar un evento"
    )

    OAUTH_CLIENT_ID: str | None = Field(default=None, description="ID del cliente")
    OAUTH_CLIENT_SECRET: str | None = Field(default=None, description="Secret del cliente")
    OAUTH_REFRESH_TOKEN: str | None = Field(default=None, description="Refresh token")
    OAUTH_TOKEN_URI: str = Field(default=..., description="Token URI de OAuth")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="GCAL_",
        extra="ignore",
    )


@lru_cache
def get_calendar_settings() -> CalendarSettings:
    """
    Guarda en caché los settings.
    Evita recrear y parsear .env en cada request.
    """
    return CalendarSettings()
