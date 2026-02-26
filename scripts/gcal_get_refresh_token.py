import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv(override=True)

# 1) MISMO scope que tu adapter.
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
]


def build_client_config_from_env() -> dict[str, dict[str, Any]]:
    client_id = os.getenv("GCAL_OAUTH_CLIENT_ID")
    client_secret = os.getenv("GCAL_OAUTH_CLIENT_SECRET")
    project_id = os.getenv("GCAL_OAUTH_PROJECT_ID", "")

    if not client_id or not client_secret:
        raise RuntimeError("Faltan GCAL_OAUTH_CLIENT_ID o GCAL_OAUTH_CLIENT_SECRET en el entorno")

    auth_uri = os.getenv("GCAL_OAUTH_AUTH_URI", "https://accounts.google.com/o/oauth2/auth")
    token_uri = os.getenv("GCAL_OAUTH_TOKEN_URI", "https://oauth2.googleapis.com/token")

    # redirect uris: comma-separated en env (opcional)
    redirect_uris_env = os.getenv("GCAL_OAUTH_REDIRECT_URIS", "http://localhost")
    redirect_uris = [u.strip() for u in redirect_uris_env.split(",") if u.strip()]

    # Estructura esperada por oauthlib:
    return {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "project_id": project_id,
            "auth_uri": auth_uri,
            "token_uri": token_uri,
            "redirect_uris": redirect_uris,
        }
    }


def main():
    client_config = build_client_config_from_env()
    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)

    # CRÍICO: para obtener refresh token
    # access_type='offline' + prompt='consent'
    creds = flow.run_local_server(
        port=0,
        access_type="offline",
        prompt="consent",
    )

    print("\n=== RESULTADO OAUTH ===")
    print("access_token:", "OK" if creds.token else None)
    print("refresh_token:", creds.refresh_token)

    if not creds.refresh_token:
        print(
            "\n⚠️ No se obtuvo refresh_token.\n"
            "Causas típicas:\n"
            "- Ya habías dado consentimiento antes (Google no devuelve refresh_token otra vez).\n"
            "- Solución: revoca el acceso en tu cuenta Google (Seguridad -> Acceso de terceros)\n"
            "  y repite, o fuerza prompt='consent' (ya lo estamos haciendo).\n"
        )

    # (Opcional) guardar token.json para reutilizar
    token_file = Path("token.json")
    token_file.write_text(creds.to_json(), encoding="utf-8")
    print(f"\nGuardado token.json en: {token_file.resolve()}")


if __name__ == "__main__":
    main()
