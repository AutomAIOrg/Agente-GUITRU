# Tests — Agente GUITRU

## Estructura

```
backend/tests/
├── conftest.py                   # Fixtures globales (engine, sesiones BD)
├── fixtures/
│   ├── __init__.py
│   └── factories.py              # MessageFactory, ReservationFactory
├── integration/
│   ├── __init__.py
│   └── test_sql_message_repository.py   # 8 tests de integración
└── unit/
    └── smoke_test.py             # 1 smoke test
```

**Total: 9 tests | ~28s | 0 redundancias**

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

## Tests de Integración (8 tests)

Archivo: `integration/test_sql_message_repository.py`

Todos usan conexión real a MySQL vía SQLAlchemy async.

| # | Clase | Test | Qué protege |
|---|---|---|---|
| 1 | `TestConnectionAndSchema` | `test_connection_and_table_schema` | Conexión a BD + tabla `messages` existe con columnas correctas |
| 2 | `TestSave` | `test_save_persists_all_fields_including_timestamp` | Todos los campos se persisten, incluido timestamp con timezone |
| 3 | `TestSave` | `test_save_multiple_messages_with_different_roles` | Múltiples saves + roles USER/ASSISTANT diferenciados |
| 4 | `TestConstraints` | `test_duplicate_id_raises_integrity_error` | PK rechaza duplicados, error se propaga |
| 5 | `TestConstraints` | `test_null_required_field_raises_error` | NOT NULL rechaza datos inválidos |
| 6 | `TestTransactions` | `test_rollback_discards_and_preserves_prior_data` | Rollback funciona, datos previos sobreviven |
| 7 | `TestEdgeCases` | `test_empty_long_and_special_content` | Cadena vacía, 10k chars, emojis, CJK, árabe |
| 8 | `TestVolume` | `test_batch_50_messages` | 50 mensajes sin degradación ni memory leaks |

## Test Unitario (1 test)

Archivo: `unit/smoke_test.py`

| Test | Qué protege |
|---|---|
| `test_smoke` | Que pytest funciona y la suite se ejecuta |

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

La conexión a BD se lee del `.env` en la raíz del proyecto.
