from pydantic import BaseModel, Field

from ...interfaces.calendar import CalendarPort
from ..config.tool_registry import ToolSpec


class CalendarUpsertIn(BaseModel):
    reservation_id: str = Field(..., description="Identificador de la reserva.")
    start_iso: str = Field(
        ...,
        description=(
            "Fecha/hora de inicio en formato ISO 8601 completo "
            "(ej: 2026-03-04T19:00:00+01:00). "
            "Debe usarse directamente el valor de checkin_iso del contexto, "
            "sin cambiar el formato."
        ),
    )
    end_iso: str = Field(
        ...,
        description=(
            "Fecha/hora de fin en formato ISO 8601 completo "
            "(ej: 2026-03-08T12:00:00+01:00). "
            "Debe usarse directamente el valor de checkout_iso del contexto, "
            "sin cambiar el formato."
        ),
    )
    title: str = Field(..., description="Título de la reserva con nombre de reserva y propiedad.")
    description: str = Field(
        ..., description="Descripción de la reserva con información extraída del contexto."
    )


class CalendarUpsertOut(BaseModel):
    event_id: str


def calendar_tool(calendar: CalendarPort) -> ToolSpec:
    def handler(input: CalendarUpsertIn) -> CalendarUpsertOut:
        event_id = calendar.upsert_reservation_event(
            reservation_id=input.reservation_id,
            start_iso=input.start_iso,
            end_iso=input.end_iso,
            title=input.title,
            description=input.description,
        )
        return CalendarUpsertOut(event_id=event_id)

    return ToolSpec(
        name="calendar_upsert_event",
        input_model=CalendarUpsertIn,
        output_model=CalendarUpsertOut,
        handler=handler,
        instructions=(
            "Las fechas y horas deben ir en formato ISO 8601 completo, por ejemplo "
            "2026-03-04T19:00:00+01:00. Usa DIRECTAMENTE los valores checkin_iso y "
            "checkout_iso del contexto para start_iso y end_iso, sin re-formatearlos. "
            "La descripción debe estar bien estructurada (con saltos de línea adecuados) y "
            "fácil de leer para el usuario, con las fechas en formato MM-DD HH:MM."
        ),
    )
