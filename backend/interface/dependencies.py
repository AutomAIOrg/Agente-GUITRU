from asyncio import Queue
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.agent.config.policies import AgentPolicies
from ..application.agent.config.tool_registry import ToolRegistry
from ..application.agent.executor import Executor
from ..application.agent.orchestrator import AgentOrchestrator
from ..application.agent.planner import Planner
from ..application.agent.tools.tool_factory import build_tool_registry
from ..application.agent.verifier import Verifier
from ..application.interfaces.calendar import CalendarPort
from ..application.interfaces.llm import LLMPort
from ..application.use_cases.generic_use_case import AgentGenericUseCase
from ..application.use_cases.process_incoming_message import ProcessIncomingMessageUseCase
from ..dependencies import get_db_session
from ..domain.entities.message import Message
from ..domain.repositories.message_repository import MessageRepository
from ..domain.repositories.reservation_repository import ReservationRepository
from ..infrastructure.adapters.calendar.google_calendar_adapter import (
    GoogleCalendarAdapter,
    GoogleCalendarConfig,
)
from ..infrastructure.adapters.calendar.google_credentials import (
    GoogleCalendarAuthConfig,
    GoogleCredentialProvider,
)
from ..infrastructure.adapters.llm.openai_adapter import OpenAIAdapter, OpenAIConfig
from ..infrastructure.config.agent_settings import AgentSettings, get_agent_settings
from ..infrastructure.config.calendar_settings import CalendarSettings, get_calendar_settings
from ..infrastructure.config.llm_settings import LLMSettings, get_llm_settings
from ..infrastructure.persistence.sql_message_repository import SQLMessageRepository
from ..infrastructure.persistence.sql_reservation_repository import SQLReservationRepository


# Repositories
def get_message_repository(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MessageRepository:
    return SQLMessageRepository(db_session=db_session)


def get_reservation_repository(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ReservationRepository:
    return SQLReservationRepository(db_session=db_session)


# Agent - LLM
def get_llm_provider(llm_settings: Annotated[LLMSettings, Depends(get_llm_settings)]) -> LLMPort:
    config = OpenAIConfig(
        api_key=llm_settings.API_KEY,
        model=llm_settings.MODEL,
        timeout_seconds=llm_settings.TIMEOUT_SECONDS,
    )
    return OpenAIAdapter(config)


# Agent - Tools and policies
def get_calendar_port(
    calendar_settings: Annotated[CalendarSettings, Depends(get_calendar_settings)],
) -> CalendarPort:
    auth = GoogleCalendarAuthConfig(
        client_id=calendar_settings.OAUTH_CLIENT_ID,
        client_secret=calendar_settings.OAUTH_CLIENT_SECRET,
        refresh_token=calendar_settings.OAUTH_REFRESH_TOKEN,
        token_uri=calendar_settings.OAUTH_TOKEN_URI,
    )
    credentials_provider = GoogleCredentialProvider(auth=auth)
    config = GoogleCalendarConfig(
        default_calendar_id=calendar_settings.CALENDAR_ID,
        timezone=calendar_settings.TIMEZONE,
        send_updates=calendar_settings.SEND_UPDATES,
    )
    return GoogleCalendarAdapter(credentials_provider=credentials_provider, config=config)


def get_tool_registry(
    calendar_port: Annotated[CalendarPort, Depends(get_calendar_port)],
) -> ToolRegistry:
    return build_tool_registry(calendar_port=calendar_port)


def get_policies(
    settings: Annotated[AgentSettings, Depends(get_agent_settings)],
) -> AgentPolicies:
    return AgentPolicies(
        max_iterations=settings.MAX_ITERATIONS,
        max_steps=settings.MAX_STEPS,
    )


# Agent
def get_planner(
    llm: Annotated[LLMPort, Depends(get_llm_provider)],
    tools: Annotated[ToolRegistry, Depends(get_tool_registry)],
    policies: Annotated[AgentPolicies, Depends(get_policies)],
) -> Planner:
    return Planner(
        llm=llm,
        tools=tools,
        policies=policies,
    )


def get_executor(
    tools: Annotated[ToolRegistry, Depends(get_tool_registry)],
) -> Executor:
    return Executor(
        tools=tools,
    )


def get_verifier(
    policies: Annotated[AgentPolicies, Depends(get_policies)],
) -> Verifier:
    return Verifier(
        policies=policies,
    )


def get_agent_orchestrator(
    planner: Annotated[Planner, Depends(get_planner)],
    executor: Annotated[Executor, Depends(get_executor)],
    verifier: Annotated[Verifier, Depends(get_verifier)],
    policies: Annotated[AgentPolicies, Depends(get_policies)],
) -> AgentOrchestrator:
    return AgentOrchestrator(
        planner=planner, executor=executor, verifier=verifier, policies=policies
    )


# Use Cases
def get_process_incoming_message_uc(
    message_repository: Annotated[MessageRepository, Depends(get_message_repository)],
    message_queue: Annotated[Queue[Message], Depends(lambda: Queue[Message]())],
) -> ProcessIncomingMessageUseCase:
    return ProcessIncomingMessageUseCase(
        message_repository=message_repository,
        message_queue=message_queue,
    )


def get_generic_uc(
    agent_orchestrator: Annotated[AgentOrchestrator, Depends(get_agent_orchestrator)],
) -> AgentGenericUseCase:
    return AgentGenericUseCase(agent_orchestrator=agent_orchestrator)
