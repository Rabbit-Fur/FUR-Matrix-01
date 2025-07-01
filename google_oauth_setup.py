import os
import pickle
from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main() -> None:
    """Run OAuth flow and store token."""
    os.makedirs("token", exist_ok=True)
    token_path = Path("token/token.pickle")
    creds = None
    if token_path.exists():
        with token_path.open("rb") as fh:
            creds = pickle.load(fh)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials/client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with token_path.open("wb") as fh:
            pickle.dump(creds, fh)
    print(f"Token saved to {token_path}")


if __name__ == "__main__":
    main()
