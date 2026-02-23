from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsDB(BaseSettings):
    """Database settings for the application."""

    DB_HOST: str = Field(
        default="localhost",
        description="Database host address",
        validation_alias=AliasChoices("DB_HOST", "MYSQL_HOST"),
    )
    DB_PORT: int = Field(
        default=3306,
        description="Database port number",
        validation_alias=AliasChoices("DB_PORT", "MYSQL_PORT"),
    )
    DB_USER: str = Field(
        default="root",
        description="Database username",
        validation_alias=AliasChoices("DB_USER", "MYSQL_USER"),
    )
    DB_PASS: SecretStr = Field(
        default=SecretStr(""),
        description="Database password",
        validation_alias=AliasChoices("DB_PASS", "MYSQL_PASSWORD"),
    )
    DB_NAME: str = Field(
        default="agente_guitru",
        description="Database name",
        validation_alias=AliasChoices("DB_NAME", "MYSQL_DATABASE"),
    )
    DB_POOL_SIZE: int = Field(default=10, description="Database connection pool size")

    DB_MAX_OVERFLOW: int = Field(
        default=20, description="Maximum overflow size for the database connection pool"
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="", extra="ignore", case_sensitive=True
    )

    @property
    def DB_URL(self) -> str:
        """Construir la URL de conexión a la base de datos MySQL."""
        password = quote_plus(self.DB_PASS.get_secret_value())
        return f"mysql+asyncmy://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


@lru_cache
def get_settings_db() -> SettingsDB:
    """Llamada para obtener la configuración de la base de datos."""
    return SettingsDB()
