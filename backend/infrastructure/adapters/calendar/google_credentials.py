from dataclasses import dataclass

from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


@dataclass(frozen=True)
class GoogleCalendarAuthConfig:
    """
    Declaración de parámetros necesarios para OAuth.
    """

    client_id: str | None = None
    client_secret: str | None = None
    refresh_token: str | None = None
    token_uri: str = "https://oauth2.googlapis.com/token"


class GoogleCredentialProvider:
    """
    Proveedor de credenciales para OAuth para Google Calendar
    """

    def __init__(self, auth: GoogleCalendarAuthConfig):
        self._auth = auth

    def get(self):
        if not (self._auth.client_id and self._auth.client_secret and self._auth.refresh_token):
            raise ValueError(
                "Error al autenticar Google Calendar:"
                + "OAuth requiere client_id + client_secret + refresh_token."
            )
        return Credentials(
            token=None,
            refresh_token=self._auth.refresh_token,
            token_uri=self._auth.token_uri,
            client_id=self._auth.client_id,
            client_secret=self._auth.client_secret,
            scopes=SCOPES,
        )
