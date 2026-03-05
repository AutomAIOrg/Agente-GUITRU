from ...shared.logging.logging_config import get_logger
from ..agent.config.models import AgentContext, AgentGoal, AgentResult
from ..agent.orchestrator import AgentOrchestrator

logger = get_logger(__name__)


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
        logger.info("Ejecutando goal: %s", goal.name)
        result = self.agent_orchestrator.run(goal, context)
        if result.ok:
            logger.info("Goal completado: %s actions=%s", goal.name, list(result.actions.keys()))
        else:
            logger.warning("Goal fallido: %s reason=%s", goal.name, result.reason)
        return result
