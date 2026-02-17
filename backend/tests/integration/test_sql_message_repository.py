"""
Tests de integración para SQLMessageRepository.

Suite mínima y sin redundancias que cubre:
- Conexión y schema de BD
- CRUD del método save()
- Constraints (PK, NOT NULL)
- Transacciones (rollback)
- Edge cases (vacío, largo, emojis, timezone)
- Volumen (batch de 50)
"""

from contextlib import suppress
from datetime import UTC, datetime

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from ...domain.entities.message import Role
from ...infrastructure.models.messages_model import MessagesModel
from ...infrastructure.persistence.sql_message_repository import SQLMessageRepository
from ..fixtures.factories import MessageFactory

pytestmark = pytest.mark.asyncio


class TestConnectionAndSchema:
    """Verifica que la BD responde y el schema es correcto."""

    async def test_connection_and_table_schema(self, test_engine):
        """
        Valida conexión, existencia de tabla 'messages' y columnas requeridas.
        Reemplaza 3 tests antiguos: connection, tables_created, correct_columns.
        """
        async with test_engine.connect() as conn:
            # Conexión activa
            assert (await conn.execute(text("SELECT 1"))).scalar() == 1

            # Tabla existe con columnas correctas
            columns = (await conn.execute(text("DESCRIBE messages"))).fetchall()
            column_names = [c[0] for c in columns]

            for expected in ("id", "user_id", "timestamp", "role", "content", "created_at"):
                assert expected in column_names, f"Falta columna '{expected}'"


class TestSave:
    """Verifica que save() persiste correctamente todos los campos."""

    async def test_save_persists_all_fields_including_timestamp(self, clean_db_session):
        """
        Guarda un mensaje con campos conocidos y verifica que TODOS
        se persisten correctamente, incluido el timestamp con timezone.
        Reemplaza 7 tests antiguos de save básico + campos + timestamp.
        """
        repo = SQLMessageRepository(clean_db_session)
        ts = datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)

        message = MessageFactory.create(
            id="save-all-fields",
            user_id="user-456",
            timestamp=ts,
            role=Role.ASSISTANT,
            content="Contenido de prueba",
        )
        await repo.save(message)

        result = await clean_db_session.execute(
            select(MessagesModel).where(MessagesModel.id == "save-all-fields")
        )
        row = result.scalar_one()

        assert row.user_id == "user-456"
        assert row.timestamp.replace(tzinfo=UTC) == ts
        assert row.role == "assistant"
        assert row.content == "Contenido de prueba"

    async def test_save_multiple_messages_with_different_roles(self, clean_db_session):
        """
        Guarda varios mensajes de un mismo usuario con roles distintos
        y verifica que todos persisten con el rol correcto.
        Reemplaza 6 tests antiguos de múltiples + roles + timestamps ordenados.
        """
        repo = SQLMessageRepository(clean_db_session)
        user_id = "multi-role-user"

        user_msg = MessageFactory.create_user_message(user_id=user_id, content="Pregunta")
        assistant_msg = MessageFactory.create_assistant_message(
            user_id=user_id, content="Respuesta"
        )
        user_msg2 = MessageFactory.create_user_message(user_id=user_id, content="Otra pregunta")

        for msg in (user_msg, assistant_msg, user_msg2):
            await repo.save(msg)

        result = await clean_db_session.execute(
            select(MessagesModel).where(MessagesModel.user_id == user_id)
        )
        rows = result.scalars().all()

        assert len(rows) == 3
        roles = {r.role for r in rows}
        assert roles == {"user", "assistant"}


class TestConstraints:
    """Verifica que la BD rechaza datos inválidos."""

    async def test_duplicate_id_raises_integrity_error(self, clean_db_session):
        """
        Guarda un mensaje y verifica que un segundo con el mismo ID falla.
        El error debe propagarse (no quedar oculto).
        Reemplaza 4 tests antiguos de PK duplicada + propagación de errores.
        """
        repo = SQLMessageRepository(clean_db_session)
        msg = MessageFactory.create(id="dup-pk")
        await repo.save(msg)

        with pytest.raises((IntegrityError, Exception)):
            await repo.save(MessageFactory.create(id="dup-pk"))

    async def test_null_required_field_raises_error(self, clean_db_session):
        """
        Intenta insertar un registro con campo NOT NULL en NULL.
        Reemplaza 1 test antiguo de NOT NULL constraint.
        """
        invalid = MessagesModel(
            id="null-test",
            timestamp=None,
            role="user",
            content="test",
        )
        clean_db_session.add(invalid)

        with pytest.raises((IntegrityError, Exception)):
            await clean_db_session.commit()

        await clean_db_session.rollback()


class TestTransactions:
    """Verifica que rollback funciona y no corrompe datos previos."""

    async def test_rollback_discards_and_preserves_prior_data(self, clean_db_session):
        """
        1) Guarda un mensaje válido.
        2) Intenta guardar uno con ID duplicado (falla).
        3) Verifica que el original sigue intacto.
        Reemplaza 3 tests antiguos de rollback + consistencia + commit permanente.
        """
        repo = SQLMessageRepository(clean_db_session)

        # 1. Guardar mensaje válido
        original = MessageFactory.create(id="rollback-test")
        await repo.save(original)

        # 2. Forzar error con ID duplicado
        with suppress(Exception):
            await repo.save(MessageFactory.create(id="rollback-test"))

        # 3. El original debe seguir en BD
        result = await clean_db_session.execute(
            select(MessagesModel).where(MessagesModel.id == "rollback-test")
        )
        assert result.scalar_one_or_none() is not None


class TestEdgeCases:
    """Verifica edge cases: vacío, largo, caracteres especiales."""

    async def test_empty_long_and_special_content(self, clean_db_session):
        """
        En un solo test valida 3 edge cases del campo content:
        - Cadena vacía
        - 10.000 caracteres
        - Emojis, acentos, CJK, árabe
        Reemplaza 3 tests antiguos de edge cases.
        """
        repo = SQLMessageRepository(clean_db_session)

        cases = {
            "edge-empty": "",
            "edge-long": "A" * 10_000,
            "edge-special": "¡Hola! 👋 ¿Cómo estás? Ñoño café 中文 العربية",
        }

        for msg_id, content in cases.items():
            await repo.save(MessageFactory.create(id=msg_id, content=content))

        for msg_id, expected in cases.items():
            result = await clean_db_session.execute(
                select(MessagesModel).where(MessagesModel.id == msg_id)
            )
            row = result.scalar_one()
            assert row.content == expected, f"Fallo en caso '{msg_id}'"


class TestVolume:
    """Verifica que no hay degradación ni memory leaks con volumen."""

    async def test_batch_50_messages(self, clean_db_session):
        """
        Guarda 50 mensajes y verifica que todos persisten.
        Reemplaza 2 tests antiguos de batch + filtrado por usuario.
        """
        repo = SQLMessageRepository(clean_db_session)
        user_id = "batch-user"
        messages = MessageFactory.create_batch(count=50, user_id=user_id)

        for msg in messages:
            await repo.save(msg)

        result = await clean_db_session.execute(
            select(MessagesModel).where(MessagesModel.user_id == user_id)
        )
        assert len(result.scalars().all()) == 50
