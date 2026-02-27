from .config.models import ToolObservation
from .config.policies import AgentPolicies


class VerificationResult:
    def __init__(self, approved: bool, notes: list[str], feedback: str | None = None):
        self.approved = approved
        self.notes = notes
        self.feedback = feedback


class Verifier:
    def __init__(self, policies: AgentPolicies):
        self.policies = policies

    def verify(self, observations: list[ToolObservation]) -> VerificationResult:
        notes: list[str] = []

        # 1. Extracción de ejecuciones fallidas de herramientas
        failed_tools = [observation for observation in observations if not observation.ok]

        # 2. Si hay fallos, reelaborar el plan
        if failed_tools:
            notes.append(
                f"Fallaron {len(failed_tools)} pasos: "
                + ", ".join(f"{f.tool}: {f.error}" for f in failed_tools)
            )
            return VerificationResult(
                approved=False,
                notes=notes,
                feedback=(
                    "Rehaz el plan evitando los pasos que fallaron"
                    " o usando alternativas permitidas."
                ),
            )

        # 3. Si no hay fallos, retornar verificación OK
        return VerificationResult(approved=True, notes=["OK"])
