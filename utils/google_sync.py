"""Helpers to sync events from Google Calendar into MongoDB."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Iterable

from config import Config
from google_calendar_sync import fetch_upcoming_events, get_calendar_service
from mongo_service import get_collection

log = logging.getLogger(__name__)


def get_service():
    """Return a Calendar API service or ``None`` if credentials are missing."""
    return get_calendar_service()


def fetch_calendar_events(
    service, calendar_id: str, time_min: datetime | None = None
) -> list[dict]:
    """Fetch events from Google Calendar."""
    return fetch_upcoming_events(
        service,
        calendar_id=calendar_id,
        time_min=time_min,
    )


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
