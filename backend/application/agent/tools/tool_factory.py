from ...interfaces.calendar import CalendarPort
from ..config.tool_registry import ToolRegistry
from .calendar import calendar_tool


def build_tool_registry(calendar_port: CalendarPort) -> ToolRegistry:
    """
    Construye el ToolRegistry del agente registrando todas las tools disponibles.
    """
    registry = ToolRegistry()

    registry.register(calendar_tool(calendar_port))

    return registry
