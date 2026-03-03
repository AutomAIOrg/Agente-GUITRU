from ..agent.config.models import AgentContext, AgentGoal, AgentResult
from ..agent.orchestrator import AgentOrchestrator


class AgentGenericUseCase:
    def __init__(
        self,
        agent_orchestrator: AgentOrchestrator,
    ):
        self.agent_orchestrator = agent_orchestrator

    def execute(self, goal: AgentGoal, context: AgentContext) -> AgentResult:
        """
        Ejecuta el multi-step reasoning agent para una tarea objetivo y un contexto dado.
        "goal" y "context" deben ser inputs ya validados y sin datos sensibles.
        """
        result = self.agent_orchestrator.run(goal, context)
        return result
