"""
Configuración global de pytest y fixtures compartidos.

Este archivo define fixtures que se comparten entre todos los tests,
especialmente fixtures para conexión a base de datos de test.
"""

import sys
from collections.abc import AsyncGenerator
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ..application.interfaces.calendar import CalendarPort
from ..application.interfaces.llm import LLMPort
from ..infrastructure.models.base import Base

# Garantizar que la raíz del proyecto esté en sys.path
# (necesario cuando el path contiene espacios y pythonpath=. de pytest.ini falla)
_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


# ==================== BASE DE DATOS DE TEST ====================


def get_test_database_url() -> str:
    """
    Construye la URL de conexión para la base de datos de test.
    """
    DB_HOST = "127.0.0.1"
    DB_PORT = 3306
    DB_USER = "user_test"
    password = "pass_test"
    db_name = "db_test"

    return f"mysql+asyncmy://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{db_name}"


@pytest_asyncio.fixture(scope="function")
async def test_engine() -> AsyncGenerator[AsyncEngine]:
    """
    Crea el engine de SQLAlchemy para la base de datos de test.
    Scope: function - Se crea para cada test (necesario para compatibilidad asyncio).

    IMPORTANTE: Usa la misma BD de producción del VPS.
    Las tablas se crean si no existen (checkfirst=True).
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

    IMPORTANTE: Limpia manualmente las tablas al final con TRUNCATE.
    SEGURIDAD VPS: Solo borra datos de test en tablas compartidas.
    """
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session

        db_name = "db_test"
        if not db_name.endswith("_test"):
            return

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
        # idempotente por reservation_id
        if reservation_id in self.store:
            return self.store[reservation_id]

        event_id = f"evt_{reservation_id}"
        self.store[reservation_id] = event_id
        return event_id


@pytest.fixture
def fake_calendar() -> InMemoryCalendar:
    return InMemoryCalendar(store={})
