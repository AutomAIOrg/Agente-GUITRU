from dataclasses import dataclass


@dataclass(frozen=True)
class AgentPolicies:
    """Reglas para controlar el agente."""

    max_iterations: int = 2
    max_steps: int = 8
    # allow_free_text_outside_window: bool = False  # en WhatsApp, normalmente templates
    # forbid_sending_full_dni: bool = True
