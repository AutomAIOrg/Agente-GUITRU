from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.agent.config.policies import AgentPolicies
from backend.application.agent.config.tool_registry import ToolRegistry
from backend.application.agent.executor import Executor
from backend.application.agent.orchestrator import AgentOrchestrator
from backend.application.agent.planner import Planner
from backend.application.agent.verifier import Verifier
from backend.application.interfaces.calendar import CalendarPort
from backend.application.interfaces.llm import LLMPort
from backend.application.use_cases.generic_use_case import AgentGenericUseCase
from backend.application.use_cases.process_incoming_message import ProcessIncomingMessageUseCase
from backend.domain.repositories.message_repository import MessageRepository
from backend.infrastructure.adapters.calendar.google_calendar_adapter import GoogleCalendarAdapter
from backend.infrastructure.adapters.llm.openai_adapter import OpenAIAdapter
from backend.infrastructure.adapters.queue.asyncio_adapter import AsyncioQueueAdapter
from backend.infrastructure.config.agent_settings import get_agent_settings
from backend.infrastructure.config.calendar_settings import CalendarSettings
from backend.infrastructure.config.llm_settings import get_llm_settings
from backend.infrastructure.config.queue_settings import get_queue_settings
from backend.infrastructure.persistence.sql_message_repository import SQLMessageRepository
from backend.infrastructure.persistence.sql_reservation_repository import SQLReservationRepository
from backend.interface.dependencies import (
    get_agent_orchestrator,
    get_calendar_adapter,
    get_executor,
    get_generic_uc,
    get_llm_provider,
    get_message_repository,
    get_planner,
    get_policies,
    get_process_incoming_message_uc,
    get_reservation_repository,
    get_tool_registry,
    get_verifier,
)

pytestmark = [
    pytest.mark.unit,
]


def test_get_message_repository():
    # Mock AsyncSession
    mock_session = AsyncMock(spec=AsyncSession)

    # Llamar a la función
    repository = get_message_repository(mock_session)

    # Verificar que devuelve una instancia de SQLMessageRepository
    assert isinstance(repository, SQLMessageRepository)
    assert repository.db_session == mock_session


def test_get_reservation_repository():
    # Mock AsyncSession
    mock_session = AsyncMock(spec=AsyncSession)

    # Llamar a la función
    repository = get_reservation_repository(mock_session)

    # Verificar que devuelve una instancia de SQLReservationRepository
    assert isinstance(repository, SQLReservationRepository)
    assert repository.db_session == mock_session


def test_get_queue_adapter():
    # Crear adaptador de la cola
    queue_settings = get_queue_settings()
    queue_adapter = AsyncioQueueAdapter(queue_settings)

    # Verificar que devuelve una instancia de AsyncioQueueAdapter
    assert isinstance(queue_adapter, AsyncioQueueAdapter)


def test_get_llm_provider():
    # Crear proveedor de LLM
    llm_settings = get_llm_settings()
    provider = get_llm_provider(llm_settings)

    # Verificar que devuelve una instancia de OpenAIAdapter
    assert isinstance(provider, OpenAIAdapter)


def test_get_calendar_adapter():
    # Mock CalendarSettings
    mock_calendar_settings = AsyncMock(
        spec=CalendarSettings(
            CALENDAR_ID="test_calendar_id",
            TIMEZONE="Europe/Madrid",
            SEND_UPDATES="none",
            OAUTH_CLIENT_ID="test_client_id",
            OAUTH_CLIENT_SECRET="test_client_secret",
            OAUTH_REFRESH_TOKEN="test_refresh_token",
            OAUTH_TOKEN_URI="https://oauth2.googleapis.com/token",
        )
    )
    provider = get_calendar_adapter(mock_calendar_settings)

    # Verificar que devuelve una instancia de GoogleCalendarAdapter
    assert isinstance(provider, GoogleCalendarAdapter)


def test_get_tool_registry():
    # Mock CalendarPort
    mock_calendar_port = AsyncMock(spec=CalendarPort)
    registry = get_tool_registry(mock_calendar_port)

    # Verificar que devuelve una instancia de ToolRegistry
    assert isinstance(registry, ToolRegistry)


def test_get_policies():
    # Crear adaptador Policies
    agent_settings = get_agent_settings()
    policies = get_policies(agent_settings)

    # Verificar que devuelve una instancia de AgentPolicies
    assert isinstance(policies, AgentPolicies)


def test_get_planner():
    # Mock dependencias
    mock_llm = AsyncMock(LLMPort)
    mock_tools = AsyncMock(ToolRegistry)
    mock_policies = AsyncMock(AgentPolicies)

    planner = get_planner(mock_llm, mock_tools, mock_policies)

    # Verificar que devuelve una instancia de Planner
    assert isinstance(planner, Planner)


def test_get_executor():
    # Mock dependencias
    mock_tools = AsyncMock(ToolRegistry)

    executor = get_executor(mock_tools)

    # Verificar que devuelve una instancia de Executor
    assert isinstance(executor, Executor)


def test_get_verifier():
    # Mock dependencias
    mock_policies = AsyncMock(AgentPolicies)

    verifier = get_verifier(mock_policies)

    # Verificar que devuelve una instancia de Verifier
    assert isinstance(verifier, Verifier)


def test_get_agent_orchestrator():
    # Mock dependencias
    mock_planner = AsyncMock(Planner)
    mock_executor = AsyncMock(Executor)
    mock_verifier = AsyncMock(Verifier)
    mock_policies = AsyncMock(AgentPolicies)

    orchestrator = get_agent_orchestrator(
        mock_planner,
        mock_executor,
        mock_verifier,
        mock_policies,
    )

    # Verificar que devuelve una instancia de Verifier
    assert isinstance(orchestrator, AgentOrchestrator)


def test_get_process_incoming_message_uc():
    # Mock dependencias
    mock_message_repository = AsyncMock(spec=MessageRepository)

    # Llamar a la función
    use_case = get_process_incoming_message_uc(
        message_repository=mock_message_repository,
    )

    # Verificar que devuelve una instancia de ProcessIncomingMessageUseCase
    assert isinstance(use_case, ProcessIncomingMessageUseCase)
    assert use_case.message_repository == mock_message_repository


def test_get_generic_uc():
    # Mock dependencias
    mock_orchestrator = AsyncMock(AgentOrchestrator)

    use_case = get_generic_uc(mock_orchestrator)

    # Verificar que devuelve una instancia de AgentGenericUseCase
    assert isinstance(use_case, AgentGenericUseCase)
