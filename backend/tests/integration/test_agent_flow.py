from ...application.agent.config.models import AgentContext, AgentGoal
from ...application.agent.config.policies import AgentPolicies
from ...application.agent.config.tool_registry import ToolRegistry
from ...application.agent.executor import Executor
from ...application.agent.orchestrator import AgentOrchestrator
from ...application.agent.planner import Planner
from ...application.agent.tools.calendar import calendar_tool
from ...application.agent.verifier import Verifier
from ..conftest import SequenceLLM


class TestAgentFlow:
    """
    Tests de integración OFFLINE (sin red):
    prueban el loop completo del agente con fakes.
    """

    def _build_agent(self, llm, calendar):
        """
        Construcción del agente.
        Helper para evitar duplicación en tests.
        """
        policies = AgentPolicies(max_steps=6, max_iterations=2)

        tools = ToolRegistry()
        tools.register(calendar_tool(calendar))

        planner = Planner(llm=llm, tools=tools, policies=policies)
        executor = Executor(tools=tools)
        verifier = Verifier(policies=policies)

        return AgentOrchestrator(
            planner=planner, executor=executor, verifier=verifier, policies=policies
        )

    def test_happy_path_crea_evento_y_devuelve_event_id(self, fake_calendar):
        """
        Caso REALISTA:
        - El planner propone 1 acción coherente (calendar_upsert_event).
        - El executor la ejecuta.
        - El verifier aprueba.
        - El agente devuelve ok=True y un event_id.
        """

        llm = SequenceLLM(
            outputs=[
                {
                    "steps": [
                        {
                            "step_id": "1",
                            "tool": "calendar_upsert_event",
                            "input": {
                                "reservation_id": "R-123",
                                "start_iso": "2026-02-01T16:00:00+01:00",
                                "end_iso": "2026-02-05T11:00:00+01:00",
                                "title": "Check-in Piso Atocha 2B",
                                "description": "Reserva R-123 (sin DNI).",
                            },
                            "rationale": "Upsert del evento en calendario",
                        }
                    ]
                }
            ]
        )

        agent = self._build_agent(llm, fake_calendar)

        goal = AgentGoal(
            name="sync_calendar",
            instructions=(
                "Crea o actualiza el evento del calendario para la reserva.No incluyas DNI."
            ),
        )
        ctx = AgentContext(
            language="es",
            reservation_id="R-123",
            property_name="Piso Atocha 2B",
            checkin_iso="2026-02-01T16:00:00+01:00",
            checkout_iso="2026-02-05T11:00:00+01:00",
            checkin_time="16:00",
        )

        result = agent.run(goal, ctx)

        # ASSERTS (lo importante)
        assert result.ok is True
        assert result.actions["event_id"] == "evt_R-123"
        assert fake_calendar.store["R-123"] == "evt_R-123"

    def test_replan_si_el_primer_plan_es_invalido_y_luego_se_corrige(self, fake_calendar):
        """
        Caso REALISTA muy importante:
        - Primera respuesta del planner tiene un error (por ejemplo falta end_iso).
        - La tool falla por validación Pydantic => el verifier rechaza.
        - El agente replanifica (2ª llamada al LLM).
        - Segunda respuesta ya es válida => ok.
        """

        llm = SequenceLLM(
            outputs=[
                # Plan 1: inválido (falta end_iso)
                {
                    "steps": [
                        {
                            "step_id": "bad-1",
                            "tool": "calendar_upsert_event",
                            "input": {
                                "reservation_id": "R-999",
                                "start_iso": "2026-02-01T16:00:00+01:00",
                                "title": "Check-in X",
                                "description": "...",
                            },
                            "rationale": "Plan con fallo",
                        }
                    ]
                },
                # Plan 2: corregido
                {
                    "steps": [
                        {
                            "step_id": "good-2",
                            "tool": "calendar_upsert_event",
                            "input": {
                                "reservation_id": "R-999",
                                "start_iso": "2026-02-01T16:00:00+01:00",
                                "end_iso": "2026-02-02T11:00:00+01:00",
                                "title": "Check-in X",
                                "description": "...",
                            },
                            "rationale": "Plan corregido",
                        }
                    ]
                },
            ]
        )

        agent = self._build_agent(llm, fake_calendar)

        goal = AgentGoal(name="sync_calendar", instructions="Upsert calendar.")
        ctx = AgentContext(
            language="es",
            reservation_id="R-999",
            property_name="Piso X",
            checkin_iso="2026-02-01T16:00:00+01:00",
            checkout_iso="2026-02-02T11:00:00+01:00",
            checkin_time="16:00",
        )

        result = agent.run(goal, ctx)

        assert result.ok is True
        assert result.actions["event_id"] == "evt_R-999"
        assert llm.calls == 2  # lo más importante: hubo replan real
