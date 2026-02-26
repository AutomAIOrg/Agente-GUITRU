from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ValidationError


class ToolError(Exception):
    pass


class ToolSpec:
    def __init__(
        self,
        name: str,
        input_model: type[BaseModel],
        output_model: type[BaseModel],
        handler: Callable[[BaseModel], BaseModel] | Callable[[Any], Any],
        instructions: str,
    ):
        self.name = name
        self.input_model = input_model
        self.output_model = output_model
        self.handler = handler
        self.instructions = instructions

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            validated_input = self.input_model.model_validate(payload)
            handler_output = self.handler(validated_input)
            validated_output = self.output_model.model_validate(handler_output)
            return validated_output.model_dump()
        except ValidationError as e:
            raise ToolError("Validación fallida en entrada/salida de herramienta.") from e
        except Exception as e:
            raise ToolError(str(e)) from e

    def json_schema(self) -> dict[str, Any]:
        return self.input_model.model_json_schema()


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec:
        if name not in self._tools:
            raise ToolError(f"Herramienta '{name}' no está registrada.")
        return self._tools[name]

    def names(self) -> list[str]:
        return list(self._tools.keys())
