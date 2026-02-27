from .config.models import AgentPlan, ToolObservation
from .config.tool_registry import ToolError, ToolRegistry


class Executor:
    def __init__(self, tools: ToolRegistry):
        self.tools = tools

    def run_plan(self, agent_plan: AgentPlan) -> list[ToolObservation]:
        """Ejecución secuencial de las herramientas que establece el plan."""
        observations: list[ToolObservation] = []

        for step in agent_plan.steps:
            tool = self.tools.get(step.tool)
            try:
                result = tool.run(step.input)
                observations.append(
                    ToolObservation(step_id=step.step_id, tool=tool.name, ok=True, output=result)
                )
            except ToolError as e:
                observations.append(
                    ToolObservation(step_id=step.step_id, tool=tool.name, ok=False, error=str(e))
                )

        return observations
