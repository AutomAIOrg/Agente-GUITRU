"""
Configuración global de pytest y fixtures compartidos.

Este archivo define fixtures que se comparten entre todos los tests,
especialmente fixtures para conexión a base de datos de test.
"""

import sys
import urllib.parse
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest_asyncio
from backend.infrastructure.config.settings_db import SettingsDB
from backend.infrastructure.models.base import Base
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Garantizar que la raíz del proyecto esté en sys.path
# (necesario cuando el path contiene espacios y pythonpath=. de pytest.ini falla)
_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# ==================== BASE DE DATOS DE TEST ====================


def get_test_database_url() -> str:
    """
    Construye la URL de conexión para la base de datos de test.

    IMPORTANTE: Para VPS con usuarios restringidos, usamos la MISMA base de datos
    que producción pero con tablas con prefijo 'test_' para diferenciarlas.
    """
    settings = SettingsDB()
    password = urllib.parse.quote_plus(settings.DB_PASS.get_secret_value())

    # Usar la MISMA base de datos (no crear una nueva)
    # El usuario del VPS probablemente no tiene permisos para crear BDs
    db_name = settings.DB_NAME

    return (
        f"mysql+asyncmy://{settings.DB_USER}:{password}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{db_name}"
    )


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
    Proporciona una sesión de base de datos limpia para cada test.
    Scope: function - Nueva sesión para cada test (aislamiento completo).

    Al final de cada test, hace rollback para limpiar los datos.
    """
    # Crear session factory
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        # Iniciar una transacción
        async with session.begin():
            yield session
            # Al salir del contexto, automáticamente hace rollback
            # Esto limpia los datos insertados durante el test
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

        # Limpiar manualmente todas las tablas con TRUNCATE (más rápido)
        from sqlalchemy import text

        # Deshabilitar FK temporalmente para limpiar
        await session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

        # Truncar todas las tablas
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(text(f"TRUNCATE TABLE `{table.name}`"))

        # Rehabilitar FK
        await session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        await session.commit()
