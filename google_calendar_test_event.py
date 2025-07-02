from __future__ import annotations

import logging
import os
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_PATH = Path(os.getenv("GOOGLE_CREDENTIALS_FILE", "/data/google_token.json"))
TIME_ZONE = "Europe/Berlin"


def load_token() -> Credentials:
    if not TOKEN_PATH.exists():
        raise FileNotFoundError(
            f"Missing token file at {TOKEN_PATH}. Run google_oauth_setup.py first."
        )
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
        else:
            raise RuntimeError("Invalid Google credentials. Re-run OAuth flow.")
    return creds


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    creds = load_token()
    service = build("calendar", "v3", credentials=creds, cache_discovery=False)

    start = datetime.now(ZoneInfo(TIME_ZONE)) + timedelta(minutes=5)
    end = start + timedelta(minutes=15)

    event = {
        "summary": "✅ FUR System Test",
        "description": "Erstellt vom automatisierten Setup.",
        "start": {"dateTime": start.isoformat(), "timeZone": TIME_ZONE},
        "end": {"dateTime": end.isoformat(), "timeZone": TIME_ZONE},
    }

    created = service.events().insert(calendarId="primary", body=event).execute()
    logging.info("Event erstellt: %s", created.get("summary"))
    logging.info("Link: %s", created.get("htmlLink"))


if __name__ == "__main__":
    main()
