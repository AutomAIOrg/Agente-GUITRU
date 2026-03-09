from ...shared.logging.logging_config import get_logger
from .config.models import AgentPlan, ToolObservation
from .config.tool_registry import ToolError, ToolRegistry

logger = get_logger(__name__)


class Executor:
    def __init__(self, tools: ToolRegistry):
        self.tools = tools

    def run_plan(self, agent_plan: AgentPlan) -> list[ToolObservation]:
        """Ejecución secuencial de las herramientas que establece el plan."""
        observations: list[ToolObservation] = []

        for step in agent_plan.steps:
            logger.debug("Ejecutando step: %s tool=%s", step.step_id, step.tool)
            try:
                tool = self.tools.get(step.tool)
            except ToolError as e:
                logger.warning("Tool no encontrada: %s error=%s", step.tool, e)
                observations.append(
                    ToolObservation(step_id=step.step_id, tool=step.tool, ok=False, error=str(e))
                )
                continue

            try:
                result = tool.run(step.input)
                logger.debug("Step completado: %s tool=%s", step.step_id, step.tool)
                observations.append(
                    ToolObservation(step_id=step.step_id, tool=tool.name, ok=True, output=result)
                )
            except ToolError as e:
                logger.warning("Error en tool %s step=%s: %s", step.tool, step.step_id, e)
                observations.append(
                    ToolObservation(step_id=step.step_id, tool=tool.name, ok=False, error=str(e))
                )

        return observations
