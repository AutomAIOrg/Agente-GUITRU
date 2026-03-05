from ...shared.logging.logging_config import get_logger
from .config.models import AgentContext, AgentGoal, AgentResult, AgentRunTrace, ToolObservation
from .config.policies import AgentPolicies
from .executor import Executor
from .planner import Planner
from .verifier import Verifier

logger = get_logger(__name__)


class AgentOrchestrator:
    def __init__(
        self,
        planner: Planner,
        executor: Executor,
        verifier: Verifier,
        policies: AgentPolicies,
    ):
        self.planner = planner
        self.executor = executor
        self.verifier = verifier
        self.policies = policies

    def run(self, goal: AgentGoal, context: AgentContext) -> AgentResult:
        """
        Ejecución del bucle del Multi-Step Reasoning Agent.
        Ejecuta los pasos: Plan > Execute > Verify.
        """
        trace = AgentRunTrace(goal=goal, context=context)
        feedback = None

        logger.info(
            "Iniciando agente: goal=%s reservation_id=%s",
            goal.name,
            context.reservation_id,
        )

        for iteration in range(self.policies.max_iterations):
            logger.debug("Iteración %d/%d", iteration + 1, self.policies.max_iterations)

            # 1. Construcción del plan para la tarea "goal".
            try:
                plan = self.planner.create_plan(goal=goal, context=context, feedback=feedback)
            except Exception as e:
                logger.warning("Error al crear el plan (iter %d): %s", iteration + 1, e)
                trace.verifier_notes.append(f"Error al crear el plan: {e}")
                feedback = (
                    "Se produjo un error al crear el plan. "
                    "Revisa el detalle del error, corrige y reintenta. "
                    f"Detalle del error: {e}"
                )
                continue
            trace.plan = plan

            # 2. Ejecución del plan.
            try:
                observations = self.executor.run_plan(agent_plan=plan)
            except Exception as e:
                logger.warning("Error al ejecutar el plan (iter %d): %s", iteration + 1, e)
                trace.verifier_notes.append(f"Error al ejecutar el plan: {e}")
                feedback = (
                    "Se produjo un error al ejecutar el plan. "
                    "Revisa el detalle del error, ajusta el plan o los parámetros y reintenta. "
                    f"Detalle del error: {e}"
                )
                continue
            trace.observations = observations

            # 3. Comprobación de la ejecución.
            verification = self.verifier.verify(observations=observations)
            trace.verifier_notes = verification.notes

            # 4. Verificación si se ha aprobado.
            if verification.approved:
                actions = self._summarize_actions(observations=observations)
                logger.info(
                    "Agente completado: goal=%s actions=%s",
                    goal.name,
                    list(actions.keys()))

                return AgentResult(ok=True, actions=actions, trace=trace)

            logger.warning("Plan rechazado (iter %d): %s", iteration + 1, verification.notes)
            feedback = verification.feedback or "Ha ocurrido un problema. Corrige el plan."

        logger.error(
            "Agente fallido tras %d iteraciones: goal=%s",
            self.policies.max_iterations,
            goal.name
        )

        return AgentResult(ok=False, reason="No aprobado tras reintentos.", trace=trace)

    def _summarize_actions(self, observations: list[ToolObservation]):
        """
        Extrae los identificadores 'event_id' y 'message_id' de las observaciones de las tools,
        y los devuelve en un diccionario de acciones.
        """
        actions = {}
        for observation in observations:
            if "event_id" in observation.output:
                actions["event_id"] = observation.output["event_id"]
            if "message_id" in observation.output:
                actions["message_id"] = observation.output["message_id"]

        return actions
