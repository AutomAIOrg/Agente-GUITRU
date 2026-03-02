# Tests — Agente GUITRU

## Estructura

```
backend/tests/
├── conftest.py                   # Fixtures globales (engine, sesiones BD)
├── e2e/                          # (Reservado para pruebas end-to-end)
├── fixtures/
│   ├── __init__.py
│   └── factories.py              # MessageFactory, ReservationFactory
├── integration/
│   ├── __init__.py
│   ├── test_sql_message_repository.py   # Tests de repositorio de mensajes
│   └── test_sql_reservation_repository.py   # Tests de repositorio de reservas
└── unit/
    ├── smoke_test.py             # Smoke test básico
    ├── application/
    │   └── uses_cases/
    │       └── test_process_incoming_message.py
    ├── domain/
    │   ├── test_entities.py
    │   └── test_value_objects.py
    ├── infrastructure/
    │   └── persistence/
    │       ├── test_sql_message_repository.py
    │       └── test_sql_reservation_repository.py
    └── interface/
        └── test_dependencies.py
```

---

## Ejecución

```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar todos los tests
pytest

# Solo integración
pytest backend/tests/integration/

# Solo un test específico
pytest backend/tests/integration/test_sql_message_repository.py::TestSave::test_save_persists_all_fields_including_timestamp

# Con output detallado
pytest -v -s
```

---

## Tests de Integración

Las pruebas de integración usan conexión real a MySQL vía SQLAlchemy async, contra una base
de datos de pruebas configurada en `.env.test`.

- `integration/test_sql_message_repository.py`: pruebas de persistencia y constraints para mensajes.
- `integration/test_sql_reservation_repository.py`: pruebas de persistencia y constraints para reservas.

## Tests Unitarios

En `backend/tests/unit/` se organizan los tests unitarios por capa:

- `unit/domain/`: tests de entidades y value objects de dominio.
- `unit/infrastructure/`: tests de repositorios SQL y adaptadores de persistencia.
- `unit/interface/`: tests de dependencias de capa de interfaz.
- `unit/application/`: tests de casos de uso.
- `unit/smoke_test.py`: smoke test básico para comprobar que la suite arranca.

---

## Fixtures

Definidas en `conftest.py`:

| Fixture | Scope | Descripción |
|---|---|---|
| `test_engine` | function | Engine async de SQLAlchemy. Crea tablas si no existen. |
| `db_session` | function | Sesión con rollback automático al final. No deja datos residuales. |
| `clean_db_session` | function | Sesión con commit real. Hace TRUNCATE al final. Usar para tests de transacciones. |

## Factories

Definidas en `fixtures/factories.py`:

| Factory | Métodos |
|---|---|
| `MessageFactory` | `.create()`, `.create_user_message()`, `.create_assistant_message()`, `.create_batch(count)` |
| `ReservationFactory` | `.create()`, `.create_batch(count)` |

---

## Configuración

La config de pytest está en `pytest.ini` (raíz del proyecto):

- `asyncio_mode = auto` — tests async sin decorador manual
- `asyncio_default_fixture_loop_scope = function` — un event loop por test
- Coverage automático con `--cov=backend`

Para la aplicación se usa `.env` en la raíz del proyecto.  
Las pruebas de integración de base de datos leen su configuración específica de `.env.test`.
