from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class CalendarSettings(BaseSettings):
    """Lee config desde variables de entorno."""

    CALENDAR_ID: str = "primary"
    TIMEZONE: str = "Europe/Madrid"
    SEND_UPDATES: Literal["none", "all", "externalOnly"] = "none"

    OAUTH_CLIENT_ID: str | None = None
    OAUTH_CLIENT_SECRET: str | None = None
    OAUTH_REFRESH_TOKEN: str | None = None
    OAUTH_TOKEN_URI: str = "https://oauth2.googleapis.com/token"

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
