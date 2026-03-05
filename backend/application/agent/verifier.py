from ...shared.logging.logging_config import get_logger
from .config.models import ToolObservation
from .config.policies import AgentPolicies

logger = get_logger(__name__)


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

        failed_tools = [observation for observation in observations if not observation.ok]

        if failed_tools:
            notes.append(
                f"Fallaron {len(failed_tools)} pasos: "
                + ", ".join(f"{f.tool}: {f.error}" for f in failed_tools)
            )
            logger.warning("Verificación rechazada: %d pasos fallidos", len(failed_tools))
            return VerificationResult(
                approved=False,
                notes=notes,
                feedback=(
                    "Rehaz el plan evitando los pasos que fallaron"
                    " o usando alternativas permitidas."
                ),
            )

        logger.debug("Verificación aprobada: %d pasos OK", len(observations))
        return VerificationResult(approved=True, notes=["OK"])
