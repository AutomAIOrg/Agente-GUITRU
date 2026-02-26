from unittest.mock import Mock

import pytest

from backend.application.agent.config.models import AgentContext, AgentGoal, AgentResult
from backend.application.agent.orchestrator import AgentOrchestrator
from backend.application.use_cases.generic_use_case import AgentGenericUseCase

pytestmark = [
    pytest.mark.unit,
]


def test_generic_use_case_calls_orchestrator_with_goal_and_context() -> None:
    """
    El caso de uso debe delegar en AgentOrchestrator.run(goal, context)
    y devolver exactamente el resultado que proporcione el orquestador.
    """
    # Arrange
    orchestrator_mock: AgentOrchestrator = Mock(spec=AgentOrchestrator)

    expected_result = AgentResult(
        ok=True,
        final_message="Operación completada",
        actions={"event_id": "evt-123"},
        reason=None,
        trace=None,
    )
    orchestrator_mock.run.return_value = expected_result

    use_case = AgentGenericUseCase(agent_orchestrator=orchestrator_mock)

    goal = AgentGoal(
        name="sync_calendar_and_confirm",
        instructions=(
            "Crea/actualiza un evento en Google Calendar para esta reserva"
            "y envía confirmación al huésped por WhatsApp usando template."
            "No incluyas DNI."
        ),
    )

    context = AgentContext(
        language="es",
        reservation_id="R-123",
        guest_phone="+34123456789",
        property_name="Casa de Pruebas",
        checkin_iso="2026-03-04T19:00:00+01:00",
        checkout_iso="2026-03-08T12:00:00+01:00",
        checkin_time="19:00",
    )

    # Act
    result = use_case.execute(goal=goal, context=context)

    # Assert
    orchestrator_mock.run.assert_called_once_with(goal, context)
    assert result is expected_result
