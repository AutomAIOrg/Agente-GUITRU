import json
from dataclasses import dataclass
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from ....application.interfaces.llm import LLMPort


@dataclass(frozen=True)
class OpenAIConfig:
    api_key: str
    model: str = "gpt-5-mini-2025-08-07"
    timeout_seconds: int = 30


class OpenAIAdapter(LLMPort):
    def __init__(self, config: OpenAIConfig):
        if not config.api_key:
            raise ValueError("LLM_OPENAI_API_KEY no establecida.")

        self._client = OpenAI(
            api_key=config.api_key,
            timeout=config.timeout_seconds,
        )
        self._model = config.model

    def generate_plan(self, system: str, user: str, schema: type[BaseModel]):
        """Devuelve un objeto validado con Pydantic (schema)."""

        try:
            # 1. Llamada a API de OpenAI para generar respuesta
            raw_response = self._client.responses.create(
                model=self._model,
                instructions=system,
                input=user,
            )
        except Exception:
            raise

        # 2. Extracción del contenido de la respuesta
        content = self._extract_response(raw_response)

        # 3. Carga de JSON string a objeto de Python
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError("El modelo no devolvió un JSON válido.") from e

        # 4. Validación del objeto Python al esquema definido
        try:
            return schema.model_validate(data)
        except ValidationError as e:
            raise ValueError(
                f"El JSON generado no cumple con el esquema {schema.__name__}: {e}"
            ) from e

    def _extract_response(self, response: Any) -> str:
        """Extrae contenido de la respuesta estructurada de OpenAI."""
        text = getattr(response, "output_text", None)
        if text:
            return text.strip()

        # Fallback si no se puede extraer.
        raise ValueError("No se pudo extraer texto del response. Revisa documentación de OpenAI.")
