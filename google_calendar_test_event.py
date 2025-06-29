from __future__ import annotations

import logging
import os
import pickle
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_PATH = os.path.join("token", "token.pickle")
TIME_ZONE = "Europe/Berlin"


def load_token() -> Credentials:
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(
            f"Missing token file at {TOKEN_PATH}. Run google_oauth_setup.py first."
        )
    with open(TOKEN_PATH, "rb") as fh:
        creds: Credentials = pickle.load(fh)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_PATH, "wb") as fh:
                pickle.dump(creds, fh)
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
