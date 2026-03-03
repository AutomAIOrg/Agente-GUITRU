"""
Configuración global de pytest y fixtures compartidos.

Este archivo define fixtures que se comparten entre todos los tests,
especialmente fixtures para conexión a base de datos de test.
"""

import sys
import urllib.parse
from collections.abc import AsyncGenerator
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio
from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ..application.interfaces.calendar import CalendarPort
from ..application.interfaces.llm import LLMPort
from ..infrastructure.config.settings_db import SettingsDB
from ..infrastructure.models.base import Base

# Garantizar que la raíz del proyecto esté en sys.path
# (necesario cuando el path contiene espacios y pythonpath=. de pytest.ini falla)
_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


# ==================== BASE DE DATOS DE TEST ====================


class SettingsDBTest(SettingsDB):
    """Configuración de base de datos específica para tests.

    Lee sus valores desde el archivo `.env.test` en la raíz del proyecto.
    """

    model_config = SettingsConfigDict(
        env_file=".env.test", env_prefix="", extra="ignore", case_sensitive=True
    )


def get_test_database_url() -> str:
    """
    Construye la URL de conexión para la base de datos de test.
    """

    settings = SettingsDBTest()
    password = urllib.parse.quote_plus(settings.DB_PASS.get_secret_value())

    return (
        f"mysql+asyncmy://{settings.DB_USER}:{password}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )


@pytest_asyncio.fixture(scope="function")
async def test_engine() -> AsyncGenerator[AsyncEngine]:
    """
    Crea el engine de SQLAlchemy para la base de datos de test definida en `.env.test`.

    - Scope: function — se crea para cada test (necesario para compatibilidad asyncio).
    - Las tablas se crean si no existen (checkfirst=True) en una base de datos cuyo
      nombre debe terminar en `_test`.
    """
    engine = create_async_engine(
        get_test_database_url(),
        echo=False,  # Cambiar a True para debug SQL
        pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    )

    # Crear tablas solo si no existen (seguro para BD compartida)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)

    yield engine

    # NO eliminamos tablas en VPS compartido - solo limpiamos datos en cada test
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    """
    Proporciona una sesión de base de datos aislada por test.
    Siempre hace rollback al finalizar.
    """
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def clean_db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    """
    Sesión de BD que hace COMMIT real (no rollback).
    Úsala solo para tests que necesitan verificar comportamiento de commit/rollback.

    IMPORTANTE: Limpia manualmente todas las tablas de la base de datos de test al final
    mediante TRUNCATE. Incluye un guard rail que aborta si DB_NAME no termina en `_test`,
    para evitar ejecutar esta limpieza sobre una base de datos real.
    """
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session

        # Guard rail de seguridad: solo limpiar si la BD es claramente de test
        settings = SettingsDBTest()
        db_name = settings.DB_NAME
        if not db_name.endswith("_test"):
            raise RuntimeError(
                f"Guard rail activado: DB_NAME={db_name!r} no termina en '_test'. "
                "Abortando limpieza de base de datos para evitar afectar datos reales."
            )

        # Limpiar manualmente todas las tablas con TRUNCATE (más rápido)
        from sqlalchemy import text

        # Deshabilitar FK temporalmente para limpiar
        await session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

        try:
            # Truncar todas las tablas
            for table in reversed(Base.metadata.sorted_tables):
                await session.execute(text(f"TRUNCATE TABLE `{table.name}`"))

            # Rehabilitar FK en la ruta de éxito
            await session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            await session.commit()

        finally:
            # Asegurar que los FK checks se reactivan incluso si algo falla
            with suppress(Exception):
                await session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))


# ==================== FAKE LLM ====================


class SequenceLLM(LLMPort):
    """
    Fake LLM: devuelve outputs (dict) en secuencia.
    Cada output se valida contra el schema Pydantic que pide el Planner.
    """

    def __init__(self, outputs: list[dict[str, Any]]):
        self._outputs = outputs
        self.calls: int = 0

    def generate_plan(self, system: str, user: str, schema: type[BaseModel]) -> BaseModel:
        if self.calls >= len(self._outputs):
            raise RuntimeError("SequenceLLM: no hay más outputs configurados")
        data = self._outputs[self.calls]
        self.calls += 1
        return schema.model_validate(data)


# ==================== FAKE CALENDAR ====================


@dataclass
class InMemoryCalendar(CalendarPort):
    """
    Fake calendar: simula upsert idempotente en memoria.
    """

    store: dict[str, str]

    def upsert_reservation_event(
        self,
        *,
        reservation_id: str,
        start_iso: str,
        end_iso: str,
        title: str,
        description: str,
        calendar_id: str | None = None,
    ) -> str:
        """
        Idempotente por reservation_id: devuelve el mismo
        event_id para el mismo reservation_id.
        """
        if reservation_id in self.store:
            return self.store[reservation_id]

        event_id = f"evt_{reservation_id}"
        self.store[reservation_id] = event_id
        return event_id


@pytest.fixture
def fake_calendar() -> InMemoryCalendar:
    return InMemoryCalendar(store={})
