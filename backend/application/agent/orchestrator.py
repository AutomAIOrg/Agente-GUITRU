from .config.models import AgentContext, AgentGoal, AgentResult, AgentRunTrace, ToolObservation
from .config.policies import AgentPolicies
from .executor import Executor
from .planner import Planner
from .verifier import Verifier


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

        for _ in range(self.policies.max_iterations):
            # 1. Construcción del plan para la tarea "goal".
            plan = self.planner.create_plan(goal=goal, context=context, feedback=feedback)
            trace.plan = plan

            # 2. Ejecución del plan.
            observations = self.executor.run_plan(agent_plan=plan)
            trace.observations = observations

            # 3. Comprobación de la ejecución.
            verification = self.verifier.verify(observations=observations)
            trace.verifier_notes = verification.notes

            # 4. Verificación si se ha aprobado.
            if verification.approved:
                actions = self._summarize_actions(observations=observations)
                return AgentResult(ok=True, actions=actions, trace=trace)

            feedback = verification.feedback or "Ha ocurrido un problema. Corrige el plan."

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
