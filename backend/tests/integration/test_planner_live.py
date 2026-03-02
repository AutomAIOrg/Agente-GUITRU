import os

import pytest
from dotenv import load_dotenv

from ...application.agent.config.models import AgentContext, AgentGoal
from ...application.agent.config.policies import AgentPolicies
from ...application.agent.config.tool_registry import ToolRegistry
from ...application.agent.planner import Planner
from ...application.agent.tools.calendar import calendar_tool
from ...infrastructure.adapters.llm.openai_adapter import OpenAIAdapter, OpenAIConfig
from ..conftest import InMemoryCalendar

load_dotenv(override=True)
pytestmark = pytest.mark.live


class TestPlannerLive:
    def test_planner_con_openai_genera_plan_valido_con_tools_permitidas(self):
        """
        LIVE test (OpenAI real):
        - Se registra solo una tool: calendar_upsert_event
          => Se fuerza al planner a elegir esa tool si está bien hecho.
        - Se verifica que el plan cumple:
          1) steps no vacío
          2) tool en allowlist
          3) input contiene campos mínimos

        Para ejecutar:
        RUN_LIVE_TESTS=1 LLM_OPENAI_API_KEY=... pytest -m live
        """
        if os.getenv("RUN_LIVE_TESTS") != "1":
            pytest.skip("Set RUN_LIVE_TESTS=1 para ejecutar tests live")

        api_key = os.getenv("LLM_OPENAI_API_KEY")
        assert api_key, "Falta LLM_OPENAI_API_KEY en el entorno"

        llm = OpenAIAdapter(OpenAIConfig(api_key=api_key))

        # Solo 1 tool permitida para que el planner no se disperse
        fake_calendar = InMemoryCalendar(store={})
        tools = ToolRegistry()
        tools.register(calendar_tool(fake_calendar))

        policies = AgentPolicies(max_steps=1, max_iterations=1)  # plan corto para test
        planner = Planner(llm=llm, tools=tools, policies=policies)

        goal = AgentGoal(
            name="sync_calendar",
            instructions=(
                "Crea/actualiza un evento en calendario usando la tool disponible. "
                "Devuelve un plan con un solo paso."
            ),
        )
        ctx = AgentContext(
            language="es",
            reservation_id="R-LIVE-001",
            property_name="Piso Test",
            checkin_iso="2026-03-01T16:00:00+01:00",
            checkout_iso="2026-03-02T11:00:00+01:00",
            checkin_time="16:00",
        )

        plan = planner.create_plan(goal, ctx)

        # Validación
        assert plan.steps, "El planner devolvió 0 steps"
        assert len(plan.steps) == 1, "Esperábamos 1 step (max_steps=1)"
        assert plan.steps[0].tool in tools.names(), "El planner usó una tool no permitida"

        inp = plan.steps[0].input
        assert inp.get("reservation_id") == "R-LIVE-001"
        assert "start_iso" in inp
        assert "end_iso" in inp
        assert "title" in inp
        assert "description" in inp
