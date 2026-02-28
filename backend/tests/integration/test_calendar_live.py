import os
from datetime import datetime, timedelta

import pytest

pytestmark = pytest.mark.live


def test_google_calendar_adapter_upsert_live():
    if os.getenv("RUN_LIVE_TESTS") != "1":
        pytest.skip("Activa RUN_LIVE_TESTS=1 para ejecutar")

    # Importa tus settings/adapters reales (ajusta rutas)
    from ...infrastructure.adapters.calendar.google_calendar_adapter import (
        GoogleCalendarAdapter,
        GoogleCalendarConfig,
    )
    from ...infrastructure.adapters.calendar.google_credentials import (
        GoogleCalendarAuthConfig,
        GoogleCredentialProvider,
    )
    from ...infrastructure.config.calendar_settings import get_calendar_settings

    settings = get_calendar_settings()
    auth = GoogleCalendarAuthConfig(
        client_id=settings.OAUTH_CLIENT_ID,
        client_secret=settings.OAUTH_CLIENT_SECRET,
        refresh_token=settings.OAUTH_REFRESH_TOKEN,
        token_uri=settings.OAUTH_TOKEN_URI,
    )
    cfg = GoogleCalendarConfig(
        default_calendar_id=settings.CALENDAR_ID,
        timezone=settings.TIMEZONE,
        send_updates=settings.SEND_UPDATES,
    )
    adapter = GoogleCalendarAdapter(credentials_provider=GoogleCredentialProvider(auth), config=cfg)
    event_id = None

    try:
        event_id = adapter.upsert_reservation_event(
            reservation_id="TEST-LIVE-001",
            start_iso=str((datetime.now() + timedelta(days=1)).isoformat()),
            end_iso=str((datetime.now() + timedelta(days=2)).isoformat()),
            title="TEST LIVE",
            description="Evento de prueba (puedes borrarlo).",
            calendar_id=settings.CALENDAR_ID,
        )

        assert event_id

    finally:
        # Cleanup: eliminar el evento creado en Google Calendar para no dejar residuos
        if event_id:
            try:
                from googleapiclient.discovery import build

                creds = GoogleCredentialProvider(auth).get()
                service = build("calendar", "v3", credentials=creds, cache_discovery=False)
                (
                    service.events()
                    .delete(
                        calendarId=settings.CALENDAR_ID,
                        eventId=event_id,
                    )
                    .execute()
                )
            except Exception:
                # No queremos que un fallo en la limpieza oculte el fallo real del test
                pass
