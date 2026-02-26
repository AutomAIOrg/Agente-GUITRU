import json

from .models import AgentContext, AgentGoal
from .policies import AgentPolicies
from .tool_registry import ToolRegistry


class PlannerPromptBuilder:
    def get_system_prompt(self, tools: ToolRegistry, policies: AgentPolicies) -> str:
        tool_list = ", ".join(tools.names())
        tool_spec = self._get_tool_spec(tools)

        print(tool_spec)

        system_prompt = (
            f"""
Eres un planner de un agente. Tu trabajo es proponer un plan de pasos usando SOLO tools permitidas.
Reglas:
- El plan consta de pasos de ejecución secuencial.
- En cada paso se ejecuta una tool. Tool call con input JSON.
- Tools permitidas: {tool_list}
- Máximo pasos: {policies.max_steps}
- No inventes datos. Usa SOLO el contexto.
"""
            """- La salida **DEBE** ser un JSON válido con **EXACTAMENTE** la siguiente estructura:
{
    "steps": [
        "step_id": str,             // Nombre de paso en el plan.
        "tool": str,                // Nombre de tool.
        "input": dict               // Inputs de tool. Seguir esquema dado en el catálogo.
        "rationale": str,           // Justificación de uso de tool.
    ]
    "max_steps": int                // Número de pasos del plan.
}
"""
            + f"""
Catálogo de tools:
{tool_spec}
"""
        )
        return system_prompt

    def get_user_prompt(
        self, goal: AgentGoal, context: AgentContext, feedback: str | None = None
    ) -> str:
        user_prompt = (
            f"GOAL: {goal.name}\n"
            f"INSTRUCTIONS: {goal.instructions}\n\n"
            f"CONTEXT: {context.model_dump()}\n\n"
        )
        if feedback:
            user_prompt += feedback
        return user_prompt

    def _get_tool_spec(self, tools: ToolRegistry):
        """Recuperar esquema de cada tool."""
        tool_catalog = []
        for name in tools.names():
            spec = tools.get(name)
            tool_catalog.append(
                {
                    "name": name,
                    "input_schema": spec.json_schema(),
                    "tool_instructions": spec.instructions,
                }
            )
        return json.dumps(tool_catalog, ensure_ascii=False)
