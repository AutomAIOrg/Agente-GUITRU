from dataclasses import dataclass
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.http import HttpError

from ....application.interfaces.calendar import CalendarPort
from .google_credentials import GoogleCredentialProvider


@dataclass(frozen=True)
class GoogleCalendarConfig:
    default_calendar_id: str = "primary"
    timezone: str = "Europe/Madrid"
    send_updates: str = "none"


class GoogleCalendarAdapter(CalendarPort):
    """Implementación de CalendarPort para Google Calendar."""

    def __init__(
        self, credentials_provider: GoogleCredentialProvider, config: GoogleCalendarConfig
    ):
        self._credentials = credentials_provider
        self._config = config

    def _get_service(self):
        creds = self._credentials.get()
        return build("calendar", "v3", credentials=creds, cache_discovery=False)

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
        calendar_id = calendar_id or self._config.default_calendar_id

        service = self._get_service()
        existing_event = self._find_event_by_reservation_id(service, calendar_id, reservation_id)

        body = self._build_event_body(
            reservation_id=reservation_id,
            title=title,
            description=description,
            start_iso=start_iso,
            end_iso=end_iso,
        )

        try:
            if existing_event:
                event_id = existing_event["id"]
                updated_event = (
                    service.events()
                    .patch(
                        calendarId=calendar_id,
                        eventId=event_id,
                        body=body,
                        sendUpdates=self._config.send_updates,
                    )
                    .execute()
                )
                return updated_event["id"]
            else:
                created_event = (
                    service.events()
                    .insert(
                        calendarId=calendar_id,
                        body=body,
                        sendUpdates=self._config.send_updates,
                    )
                    .execute()
                )
                return created_event["id"]

        except HttpError as e:
            raise RuntimeError(f"Google Calendar API error: {e}") from e

    def _find_event_by_reservation_id(
        self, service, calendar_id: str, reservation_id: str
    ) -> dict[str, Any] | None:
        """
        Búsqueda idempotente por identificador de reserva
        (usando privateExtendedProperty=reservation_id=<id>).
        """
        prop = f"reservation_id={reservation_id}"

        response = (
            service.events()
            .list(
                calendarId=calendar_id,
                privateExtendedProperty=prop,
                maxResults=1,
                singleEvents=True,
                showDeleted=False,
            )
            .execute()
        )

        items = response.get("items", [])
        return items[0] if items else None

    def _build_event_body(
        self,
        reservation_id: str,
        title: str,
        description: str,
        start_iso: str,
        end_iso: str,
    ) -> dict[str, Any]:
        """
        Construcción de Event Resource mínimo.

        Se guarda reservation_id en extendedProperties.private para upsert fiable.
        Google recomienda extendedProperties para metadata específica de la app.
        """

        return {
            "summary": title,
            "description": description,
            "start": {
                "dateTime": start_iso,
                "timeZone": self._config.timezone,
            },
            "end": {
                "dateTime": end_iso,
                "timeZone": self._config.timezone,
            },
            "extendedProperties": {
                "private": {
                    "reservation_id": reservation_id,
                    "source": "whatsapp-ai-agent",
                }
            },
        }
