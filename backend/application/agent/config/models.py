from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field

ToolName = str


class AgentGoal(BaseModel):
    """Objetivo del agente en su tarea."""

    name: str
    instructions: str


class AgentContext(BaseModel):
    """Contexto del agente, con datos verificados y sin información sensible."""

    language: Literal["es", "en"]
    reservation_id: str
    guest_phone: str
    property_name: str
    checkin_iso: str
    checkout_iso: str
    checkin_time: str


class PlanStep(BaseModel):
    """Paso del plan. Llama a una tool concreta con un payload JSON."""

    step_id: str
    tool: ToolName
    input: dict[str, Any] = Field(default_factory=dict)
    rationale: str = Field(..., description="Razonamiento de por qué hacer este paso.")


class AgentPlan(BaseModel):
    """Plan diseñado por el agente para realizar una tarea."""

    steps: list[PlanStep]
    max_steps: Annotated[int, Field(ge=1, le=12)] = 8


class ToolObservation(BaseModel):
    """Revisión de la ejecución de una tool."""

    step_id: str
    tool: ToolName
    ok: bool
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class AgentRunTrace(BaseModel):
    """Trazas del agente al realizar la tarea."""

    goal: AgentGoal
    context: AgentContext
    plan: AgentPlan | None = None
    observations: list[ToolObservation] = Field(default_factory=list)
    verifier_notes: list[str] = Field(default_factory=list)


class AgentResult(BaseModel):
    """Resultado de ejecutar la tarea."""

    ok: bool
    final_message: str | None = None
    actions: dict[str, Any] = Field(default_factory=dict)
    reason: str | None = None
    trace: AgentRunTrace | None = None
