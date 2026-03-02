import os
import uuid
from contextlib import suppress
from datetime import datetime, timedelta

import pytest
from dotenv import load_dotenv
from googleapiclient.discovery import build

from ...application.agent.config.models import AgentContext, AgentGoal
from ...application.agent.config.policies import AgentPolicies
from ...application.agent.config.tool_registry import ToolRegistry
from ...application.agent.executor import Executor
from ...application.agent.orchestrator import AgentOrchestrator
from ...application.agent.planner import Planner
from ...application.agent.tools.calendar import calendar_tool
from ...application.agent.verifier import Verifier
from ...infrastructure.adapters.calendar.google_calendar_adapter import (
    GoogleCalendarAdapter,
    GoogleCalendarConfig,
)
from ...infrastructure.adapters.calendar.google_credentials import (
    GoogleCalendarAuthConfig,
    GoogleCredentialProvider,
)
from ...infrastructure.adapters.llm.openai_adapter import OpenAIAdapter, OpenAIConfig

# ===== Ajusta estos imports a tus rutas reales =====
from ...infrastructure.config.calendar_settings import get_calendar_settings
from ...infrastructure.config.llm_settings import get_llm_settings

# ================================================

load_dotenv(override=True)
pytestmark = [pytest.mark.live, pytest.mark.e2e]


class TestAgentCalendarE2E:
    """
    E2E LIVE:
    - Planner real (OpenAI) genera un plan válido
    - Executor ejecuta la tool real de Calendar (GoogleCalendarAdapter)
    - Verificamos el evento real en Google Calendar con events.get(...)
    """

    def test_agent_crea_evento_en_google_calendar_e2e(self):
        # --- gating (evitar coste/flakiness en CI por accidente) ---
        if os.getenv("RUN_LIVE_TESTS", "0") != "1":
            pytest.skip("Activa RUN_LIVE_TESTS=1 para ejecutar tests live")
        if os.getenv("RUN_E2E_TESTS", "0") != "1":
            pytest.skip("Activa RUN_E2E_TESTS=1 para ejecutar tests e2e")

        # --- settings ---
        cal_settings = get_calendar_settings()
        llm_settings = get_llm_settings()

        # --- LLM real ---
        # Ajusta según cómo guardes model en settings/env:
        llm = OpenAIAdapter(
            OpenAIConfig(
                api_key=llm_settings.API_KEY,
                model=llm_settings.MODEL,
                timeout_seconds=llm_settings.TIMEOUT_SECONDS,
            )
        )

        # --- Calendar real (OAuth usuario) ---
        auth = GoogleCalendarAuthConfig(
            client_id=cal_settings.OAUTH_CLIENT_ID,
            client_secret=cal_settings.OAUTH_CLIENT_SECRET,
            refresh_token=cal_settings.OAUTH_REFRESH_TOKEN,
            token_uri=cal_settings.OAUTH_TOKEN_URI,
        )
        calendar_adapter = GoogleCalendarAdapter(
            credentials_provider=GoogleCredentialProvider(auth),
            config=GoogleCalendarConfig(
                default_calendar_id=cal_settings.CALENDAR_ID,
                timezone=cal_settings.TIMEZONE,
                send_updates=cal_settings.SEND_UPDATES,
            ),
        )

        # --- Agent wiring (igual que tu build_agent) ---
        policies = AgentPolicies(max_steps=2, max_iterations=2)
        tools = ToolRegistry()
        tools.register(calendar_tool(calendar_adapter))

        planner = Planner(llm=llm, tools=tools, policies=policies)
        executor = Executor(tools=tools)
        verifier = Verifier(policies=policies)
        agent = AgentOrchestrator(
            planner=planner, executor=executor, verifier=verifier, policies=policies
        )

        # --- Contexto realista + ID único para evitar colisiones ---
        reservation_id = f"E2E-{uuid.uuid4().hex[:8]}"

        # OJO: usa ISO con tz para evitar problemas de timezone
        now = datetime.now().astimezone()
        start_iso = str((now + timedelta(days=3)).isoformat())
        end_iso = str((now + timedelta(days=7)).isoformat())

        goal = AgentGoal(
            name="sync_calendar",
            instructions=(
                "Crea o actualiza un evento de calendario usando SOLO la tool disponible. "
                "No inventes datos. Usa exactamente el reservation_id del contexto. "
                "No incluyas DNI ni datos sensibles."
            ),
        )
        ctx = AgentContext(
            language="es",
            reservation_id=reservation_id,
            property_name="Piso Test E2E",
            checkin_iso=start_iso,
            checkout_iso=end_iso,
            checkin_time="16:00",
        )

        # Construimos un cliente de Calendar API con las MISMAS credenciales usadas en el adapter
        creds = GoogleCredentialProvider(auth).get()
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        event_id = None

        try:
            # --- Act: llamada end-to-end al agente ---
            result = agent.run(goal, ctx)

            # --- Assert 1: el agente completó y devolvió event_id ---
            assert result.ok is True, f"Agent result not ok: {result}"
            event_id = result.actions.get("event_id")
            assert event_id, "El agente no devolvió event_id en result.actions"

            # --- Assert 2: verificar en Google Calendar que evento existe y tiene metadata estable

            event = (
                service.events()
                .get(
                    calendarId=cal_settings.CALENDAR_ID,
                    eventId=event_id,
                )
                .execute()
            )

            # Validación estable (no depende del LLM): reservation_id en extendedProperties
            ext = (event.get("extendedProperties") or {}).get("private") or {}
            assert ext.get("reservation_id") == reservation_id, (
                f"extendedProperties.private.reservation_id no coincide. "
                f"Esperado={reservation_id}, Actual={ext.get('reservation_id')}"
            )

        finally:
            # Cleanup: eliminar el evento creado en Google Calendar para no dejar residuos
            if event_id:
                with suppress(Exception):
                    service.events().delete(
                        calendarId=cal_settings.CALENDAR_ID,
                        eventId=event_id,
                    ).execute()
