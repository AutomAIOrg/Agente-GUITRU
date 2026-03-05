from typing import cast

from pydantic import BaseModel, Field

from ...shared.logging.logging_config import get_logger
from ..interfaces.llm import LLMPort
from .config.models import AgentContext, AgentGoal, AgentPlan, PlanStep
from .config.policies import AgentPolicies
from .config.prompt_builders import PlannerPromptBuilder
from .config.tool_registry import ToolRegistry

logger = get_logger(__name__)


class _PlannerOutput(BaseModel):
    steps: list[PlanStep] = Field(min_length=1, max_length=12)


class Planner:
    """Agente encargado de elaborar un plan para resolver la tarea que pida el usuario."""

    def __init__(
        self,
        llm: LLMPort,
        tools: ToolRegistry,
        policies: AgentPolicies,
    ):
        self.llm = llm
        self.tools = tools
        self.policies = policies

    def create_plan(
        self, goal: AgentGoal, context: AgentContext, feedback: str | None = None
    ) -> AgentPlan:
        """Creación del plan para la tarea a desarrollar."""

        logger.debug("Creando plan: goal=%s feedback=%s", goal.name, bool(feedback))

        # 1. Construcción de prompts
        prompt_builder = PlannerPromptBuilder()
        system_prompt = prompt_builder.get_system_prompt(self.tools, self.policies)
        user_prompt = prompt_builder.get_user_prompt(goal, context, feedback)

        # 2. Llamada a LLM
        plan = cast(
            _PlannerOutput,
            self.llm.generate_plan(system=system_prompt, user=user_prompt, schema=_PlannerOutput),
        )

        # 3. Construcción de AgentPlan y verificación de Policies
        agent_plan = AgentPlan(steps=plan.steps, max_steps=self.policies.max_steps)
        if len(agent_plan.steps) > self.policies.max_steps:
            agent_plan.steps = agent_plan.steps[: self.policies.max_steps]

        # 4. Retornar plan
        logger.info("Plan creado: %d pasos", len(agent_plan.steps))
        return agent_plan
