import os
from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main() -> None:
    """Run OAuth flow and store token as JSON."""
    token_path = Path(os.getenv("GOOGLE_CREDENTIALS_FILE", "/data/google_token.json"))
    creds = None
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception:  # noqa: BLE001
            creds = None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv("GOOGLE_CLIENT_CONFIG"),
                SCOPES,
            )
            creds = flow.run_local_server(port=0)
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json())
    print(f"Token saved to {token_path}")


if __name__ == "__main__":
    main()
