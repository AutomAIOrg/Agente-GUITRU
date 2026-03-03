from abc import ABC, abstractmethod


class CalendarPort(ABC):
    @abstractmethod
    def upsert_reservation_event(
        self,
        *,
        reservation_id: str,
        start_iso: str,
        end_iso: str,
        title: str,
        description: str,
        calendar_id: str | None = None,
    ) -> str:
        """Crea o actualiza un evento en el calendario, y devuelve event_id."""
        pass
