"""Helpers to sync events from Google Calendar into MongoDB."""

from __future__ import annotations

import logging
import os
import pickle
from datetime import datetime, timezone
from typing import Iterable

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from config import Config
from mongo_service import get_collection

TOKEN_PATH = os.path.join("token", "token.pickle")

log = logging.getLogger(__name__)


def _load_token() -> Credentials | None:
    """Load OAuth token from pickle file."""
    if not os.path.exists(TOKEN_PATH):
        log.warning("Google token missing – run google_oauth_setup.py")
        return None
    with open(TOKEN_PATH, "rb") as fh:
        creds: Credentials = pickle.load(fh)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, "wb") as fh:
            pickle.dump(creds, fh)
    return creds


def get_service():
    """Return a Calendar API service or ``None`` if credentials are missing."""
    creds = _load_token()
    if not creds:
        return None
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def fetch_calendar_events(
    service, calendar_id: str, time_min: datetime | None = None
) -> list[dict]:
    """Fetch events from Google Calendar."""
    if not service:
        return []
    events: list[dict] = []
    page_token = None
    params = {
        "calendarId": calendar_id,
        "singleEvents": True,
        "orderBy": "updated",
    }
    if time_min:
        params["timeMin"] = time_min.isoformat() + "Z"
    while True:
        if page_token:
            params["pageToken"] = page_token
        result = service.events().list(**params).execute()
        events.extend(result.get("items", []))
        page_token = result.get("nextPageToken")
        if not page_token:
            break
    return events


def _parse_datetime(info: dict | None) -> datetime | None:
    """Return ``datetime`` from Google date dict or ``None`` if invalid."""
    if not info:
        return None
    value = info.get("dateTime") or info.get("date")
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value.replace("Z", "+00:00")
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def import_events(events: Iterable[dict]) -> None:
    """Upsert events into MongoDB."""
    collection = get_collection("events")
    for e in events:
        start_dt = _parse_datetime(e.get("start"))
        end_dt = _parse_datetime(e.get("end"))
        event_time = start_dt
        if event_time:
            if event_time.tzinfo is None:
                event_time = event_time.replace(tzinfo=timezone.utc)
            else:
                event_time = event_time.astimezone(timezone.utc)

        doc = {
            "title": e.get("summary", "No Title"),
            "description": e.get("description"),
            "location": e.get("location"),
            "google_event_id": e.get("id"),
            "updated": e.get("updated"),
            "start": start_dt,
            "end": end_dt,
            "event_time": event_time,
            "source": "google",
        }
        if not doc["google_event_id"]:
            continue
        collection.update_one(
            {"google_event_id": doc["google_event_id"]}, {"$set": doc}, upsert=True
        )


def sync_google_calendar() -> None:
    """Synchronize events from Google Calendar into MongoDB."""
    calendar_id = Config.GOOGLE_CALENDAR_ID
    if not calendar_id:
        log.warning("GOOGLE_CALENDAR_ID not set – skipping Google sync")
        return
    service = get_service()
    if not service:
        return
    events = fetch_calendar_events(service, calendar_id)
    if events:
        import_events(events)
        log.info("Imported %s Google calendar events", len(events))
    else:
        log.info("No Google calendar events fetched")
