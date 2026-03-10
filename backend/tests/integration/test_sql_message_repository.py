"""
Tests de integración para SQLMessageRepository.

Suite esencial alineada con el contrato actual del repositorio:
- persistencia básica
- idempotencia por provider_message_id
- propagación de IntegrityError cuando el conflicto NO es el esperado
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from ...domain.entities.message import Message, Role
from ...infrastructure.models.messages_model import MessagesModel
from ...infrastructure.persistence.sql_message_repository import SQLMessageRepository

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.integration,
    pytest.mark.repository,
    pytest.mark.database,
]


class TestConnectionAndSchema:
    async def test_connection_and_table_schema(self, test_engine):
        async with test_engine.connect() as conn:
            assert (await conn.execute(text("SELECT 1"))).scalar() == 1

            columns = (await conn.execute(text("DESCRIBE messages"))).fetchall()
            column_names = [c[0] for c in columns]

            for expected in (
                "id",
                "user_id",
                "provider_message_id",
                "timestamp",
                "role",
                "content",
                "created_at",
            ):
                assert expected in column_names, f"Falta columna '{expected}'"


class TestSave:
    async def test_save_returns_true_and_persists_message(self, clean_db_session):
        repo = SQLMessageRepository(clean_db_session)

        message = Message(
            id=uuid4().hex,
            user_id="user-123",
            provider_message_id="wamid.persist.ok",
            timestamp=datetime(2026, 3, 10, 12, 0, 0, tzinfo=UTC),
            role=Role.USER,
            content="Contenido de prueba",
        )

        saved = await repo.save_if_new(message)

        assert saved is True

        result = await clean_db_session.execute(
            select(MessagesModel).where(MessagesModel.id == message.id)
        )
        row = result.scalar_one()

        assert row.user_id == "user-123"
        assert row.provider_message_id == "wamid.persist.ok"
        assert row.timestamp.replace(tzinfo=UTC) == message.timestamp
        assert row.role == "user"
        assert row.content == "Contenido de prueba"


class TestIdempotency:
    async def test_duplicate_provider_message_id_returns_false_and_does_not_insert_second_row(
        self, clean_db_session
    ):
        repo = SQLMessageRepository(clean_db_session)

        provider_message_id = f"wamid-{uuid4().hex}"

        first = Message(
            id=uuid4().hex,
            user_id="user-1",
            provider_message_id=provider_message_id,
            timestamp=datetime(2026, 3, 10, 12, 0, 0, tzinfo=UTC),
            role=Role.USER,
            content="Primer mensaje",
        )
        second = Message(
            id=uuid4().hex,
            user_id="user-1",
            provider_message_id=provider_message_id,
            timestamp=datetime(2026, 3, 10, 12, 1, 0, tzinfo=UTC),
            role=Role.USER,
            content="Duplicado",
        )

        assert await repo.save_if_new(first) is True
        assert await repo.save_if_new(second) is False

        result = await clean_db_session.execute(
            select(MessagesModel).where(MessagesModel.provider_message_id == provider_message_id)
        )
        rows = result.scalars().all()

        assert len(rows) == 1
        assert rows[0].content == "Primer mensaje"


class TestConstraints:
    async def test_duplicate_primary_key_propagates_integrity_error(self, clean_db_session):
        repo = SQLMessageRepository(clean_db_session)

        duplicate_id = uuid4().hex

        first = Message(
            id=duplicate_id,
            user_id="user-1",
            provider_message_id=f"wamid-{uuid4().hex}",
            timestamp=datetime(2026, 3, 10, 12, 0, 0, tzinfo=UTC),
            role=Role.USER,
            content="Original",
        )
        second = Message(
            id=duplicate_id,
            user_id="user-2",
            provider_message_id=f"wamid-{uuid4().hex}",
            timestamp=datetime(2026, 3, 10, 12, 1, 0, tzinfo=UTC),
            role=Role.USER,
            content="Conflicto de PK",
        )

        assert await repo.save_if_new(first) is True

        with pytest.raises(IntegrityError, match=r"Duplicate entry|UNIQUE"):
            await repo.save_if_new(second)
