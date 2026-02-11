from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsDB(BaseSettings):
    """Database settings for the application."""

    DB_HOST: str = Field(default="localhost", description="Database host address")
    DB_PORT: int = Field(default=3306, description="Database port number")
    DB_USER: str = Field(default="root", description="Database username")
    DB_PASS: SecretStr = Field(default="", description="Database password")
    DB_NAME: str = Field(default="agente_guitru", description="Database name")
    DB_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(
        default=20, description="Maximum overflow size for the database connection pool"
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="", extra="ignore", case_sensitive=True
    )


@lru_cache
def get_settings_db() -> SettingsDB:
    """Llamada para obtener la configuración de la base de datos."""
    return SettingsDB()
