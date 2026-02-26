import os

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

    event_id = adapter.upsert_reservation_event(
        reservation_id="TEST-LIVE-001",
        start_iso="2026-02-01T16:00:00+01:00",
        end_iso="2026-02-01T17:00:00+01:00",
        title="TEST LIVE",
        description="Evento de prueba (puedes borrarlo).",
        calendar_id=settings.CALENDAR_ID,
    )

    assert event_id
