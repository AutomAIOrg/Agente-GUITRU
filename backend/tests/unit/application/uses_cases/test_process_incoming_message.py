from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.application.dtos.whatsapp_incoming_message import WhatsappIncomingMessage
from backend.application.use_cases.process_incoming_message import ProcessIncomingMessageUseCase
from backend.domain.entities.message import Role

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.unit,
]


class DummyUoW:
    def __init__(self, messages_repo):
        self.messages = messages_repo
        self.commit = AsyncMock()
        self.rollback = AsyncMock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None


def _build_incoming_message(
    *, content: str = "Hola", message_id: str = "wamid.TEST"
) -> WhatsappIncomingMessage:
    return WhatsappIncomingMessage(
        message_id=message_id,
        from_phone="34600000000",
        timestamp=int(datetime.now(tz=UTC).timestamp()),
        content=content,
    )


async def test_execute_valid_message_saves_and_commits():
    repo = AsyncMock()
    repo.save_if_new.return_value = True

    uow = DummyUoW(repo)
    uow_factory = MagicMock(return_value=uow)

    use_case = ProcessIncomingMessageUseCase(uow_factory=uow_factory)

    incoming = _build_incoming_message(content="Hello!")

    result = await use_case.execute(incoming)

    assert result is not None
    assert result.user_id == "34600000000"
    assert result.provider_message_id == "wamid.TEST"
    assert result.role == Role.USER
    assert result.content == "Hello!"

    uow_factory.assert_called_once()
    repo.save_if_new.assert_awaited_once()
    saved_message = repo.save_if_new.await_args.args[0]
    assert saved_message.user_id == "34600000000"
    assert saved_message.provider_message_id == "wamid.TEST"
    assert saved_message.content == "Hello!"

    uow.commit.assert_awaited_once()


async def test_execute_returns_none_when_repository_reports_duplicate():
    repo = AsyncMock()
    repo.save_if_new.return_value = False

    uow = DummyUoW(repo)
    uow_factory = MagicMock(return_value=uow)

    use_case = ProcessIncomingMessageUseCase(uow_factory=uow_factory)

    incoming = _build_incoming_message(message_id="wamid.DUPLICATE")

    result = await use_case.execute(incoming)

    assert result is None
    uow_factory.assert_called_once()
    repo.save_if_new.assert_awaited_once()
    uow.commit.assert_not_awaited()


async def test_execute_invalid_message_returns_none_without_opening_uow():
    repo = AsyncMock()
    uow = DummyUoW(repo)
    uow_factory = MagicMock(return_value=uow)

    use_case = ProcessIncomingMessageUseCase(uow_factory=uow_factory)

    incoming = _build_incoming_message(content="")

    result = await use_case.execute(incoming)

    assert result is None
    uow_factory.assert_not_called()
    repo.save_if_new.assert_not_called()
    uow.commit.assert_not_awaited()
