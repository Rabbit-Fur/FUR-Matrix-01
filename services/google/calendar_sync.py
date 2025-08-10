import logging
import os
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from flask import current_app, has_app_context
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from mongo_service import get_collection
from utils.time_utils import parse_calendar_datetime


class SyncTokenExpired(Exception):
    """Raised when the Google OAuth token is missing or invalid."""


# Logging setup
LOG_PATH = Path("logs")
logger = logging.getLogger(__name__)
_logging_initialized = False


def init_logging() -> None:
    """Initialize file handler for this module's logger once."""
    global _logging_initialized
    if _logging_initialized:
        return
    LOG_PATH.mkdir(exist_ok=True)
    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        handler = logging.FileHandler(LOG_PATH / "calendar_sync.log")
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    _logging_initialized = True


init_logging()


def _token_path() -> Path:
    """Return the configured OAuth token storage path."""
    if has_app_context():
        cfg = current_app.config
        path = cfg.get("GOOGLE_TOKEN_STORAGE_PATH") or cfg.get("GOOGLE_CREDENTIALS_FILE")
        if path:
            return Path(path)
    env_path = os.environ.get("GOOGLE_TOKEN_STORAGE_PATH") or os.environ.get(
        "GOOGLE_CREDENTIALS_FILE"
    )
    return Path(env_path or "/data/google_token.json")


def _get_token_collection():
    """Return the MongoDB collection used for sync tokens."""
    return get_collection("calendar_tokens")


def _load_sync_token() -> str | None:
    """Fetch the previously stored sync token.

    Returns
    -------
    str | None
        The last sync token from MongoDB or ``None`` when not available.
    """
    col = _get_token_collection()
    if not hasattr(col, "find_one"):
        return None
    doc = col.find_one({"_id": "google"})
    return doc.get("token") if doc else None


def _store_sync_token(token: str) -> None:
    """Persist a sync token for later incremental synchronization.

    Parameters
    ----------
    token:
        The sync token returned by the Google Calendar API.

    Returns
    -------
    None
        This function stores the token and does not return a value.
    """
    col = _get_token_collection()
    if hasattr(col, "update_one"):
        col.update_one({"_id": "google"}, {"$set": {"token": token}}, upsert=True)


_warned_once = False


def load_credentials() -> Optional[Credentials]:
    """Load stored credentials from JSON and refresh if needed."""
    global _warned_once
    path = _token_path()
    if not path.exists():
        if not _warned_once:
            logger.warning("No Google credentials found at %s", path)
            _warned_once = True
        return None
    try:
        info = json.loads(path.read_text())
    except Exception:  # noqa: BLE001
        logger.exception("Failed to read credentials JSON")
        return None

    required = {"client_id", "client_secret", "refresh_token"}
    keys = set(info)
    if not required.issubset(keys):
        if ("installed" in info or "web" in info) and not _warned_once:
            logger.warning(
                "Credentials file %s looks like an OAuth client config, not a saved token",
                path,
            )
            _warned_once = True
        elif not _warned_once:
            missing = ", ".join(sorted(required - keys))
            logger.warning("Credentials file %s missing required keys: %s", path, missing)
            _warned_once = True
        return None

    try:
        scopes = (
            current_app.config.get(
                "GOOGLE_CALENDAR_SCOPES",
                ["https://www.googleapis.com/auth/calendar.readonly"],
            )
            if has_app_context()
            else os.environ.get(
                "GOOGLE_CALENDAR_SCOPES",
                "https://www.googleapis.com/auth/calendar.readonly",
            ).split(",")
        )
        creds = Credentials.from_authorized_user_info(info, scopes)
        if creds.expired and creds.refresh_token:
            logger.info("Refreshing Google credentials")
            creds.refresh(Request())
            path.write_text(creds.to_json())
        _warned_once = False
        return creds
    except Exception:  # noqa: BLE001
        logger.exception("Failed to load or refresh credentials")
        return None


_SERVICE: Any | None = None


def get_calendar_service():
    """Return a cached Google Calendar API service."""
    global _SERVICE
    if _SERVICE:
        return _SERVICE
    creds = load_credentials()
    if not creds:
        raise SyncTokenExpired("Missing Google OAuth token")
    try:
        _SERVICE = build("calendar", "v3", credentials=creds, cache_discovery=False)
        return _SERVICE
    except Exception:  # noqa: BLE001
        logger.exception("Failed to build Google Calendar service")
        raise


def fetch_upcoming_events(
    service: Any | None = None,
    *,
    calendar_id: Optional[str] = None,
    time_min: Optional[datetime] = None,
    time_max: Optional[datetime] = None,
    max_results: int = 2500,
) -> list[dict]:
    """Fetch events from Google Calendar."""
    service = service or get_calendar_service()
    if calendar_id is None:
        if has_app_context():
            calendar_id = current_app.config.get("GOOGLE_CALENDAR_ID")
        if not calendar_id:
            logger.warning("GOOGLE_CALENDAR_ID not configured")
            return []

    params = {
        "calendarId": calendar_id,
        "singleEvents": True,
        "orderBy": "startTime",
        "maxResults": max_results,
    }
    if time_min:
        params["timeMin"] = time_min.astimezone(timezone.utc).isoformat()
    if time_max:
        params["timeMax"] = time_max.astimezone(timezone.utc).isoformat()

    events: list[dict] = []
    page_token = None
    try:
        while True:
            if page_token:
                params["pageToken"] = page_token
            result = service.events().list(**params).execute()
            events.extend(result.get("items", []))
            page_token = result.get("nextPageToken")
            if not page_token:
                break
    except Exception:  # noqa: BLE001
        logger.exception("Failed to fetch events from Google Calendar")
    return events


def list_upcoming_events(max_results: int = 10) -> list[dict]:
    """Return upcoming Google Calendar events."""
    now = datetime.utcnow().astimezone(timezone.utc)
    return fetch_upcoming_events(time_min=now, max_results=max_results)


def _build_doc(event: dict) -> dict:
    """Build a MongoDB document representation for a calendar event.

    Parameters
    ----------
    event:
        Raw event data from the Google Calendar API.

    Returns
    -------
    dict
        Document compatible with the ``calendar_events`` collection.
    """
    start_dt = parse_calendar_datetime(event.get("start"))
    end_dt = parse_calendar_datetime(event.get("end"))
    return {
        "google_id": event.get("id"),
        "title": event.get("summary", "No Title"),
        "description": event.get("description"),
        "location": event.get("location"),
        "updated": event.get("updated"),
        "start": start_dt,
        "end": end_dt,
        "event_time": start_dt,
        "source": "google",
        "status": event.get("status"),
    }


def sync_to_mongodb(collection: str = "calendar_events") -> int:
    """Fetch events and upsert them into MongoDB."""
    service = get_calendar_service()
    if has_app_context():
        calendar_id = current_app.config.get("GOOGLE_CALENDAR_ID", "primary")
    else:
        calendar_id = os.environ.get("GOOGLE_CALENDAR_ID", "primary")
    events = fetch_upcoming_events(service=service, calendar_id=calendar_id)
    if not events:
        logger.info("No events returned from calendar")
        return 0

    col = get_collection(collection)
    count = 0
    for ev in events:
        doc = _build_doc(ev)
        if not doc["google_id"]:
            continue
        try:
            col.update_one({"google_id": doc["google_id"]}, {"$set": doc}, upsert=True)
            count += 1
        except Exception:
            logger.exception("Failed to sync event %s", doc.get("google_id"))
    logger.info("Synced %s events to MongoDB", count)
    return count


def create_test_event(
    summary: str = "✅ Bot verbunden", *, minutes_from_now: int = 5
) -> Optional[dict]:
    """Create a small test event in the primary calendar."""
    service = get_calendar_service()
    if not service:
        logger.warning("No calendar service – cannot create test event")
        return None
    start = datetime.utcnow() + timedelta(minutes=minutes_from_now)
    end = start + timedelta(minutes=15)
    event = {
        "summary": summary,
        "start": {"dateTime": start.isoformat() + "Z"},
        "end": {"dateTime": end.isoformat() + "Z"},
    }
    try:
        created = service.events().insert(calendarId="primary", body=event).execute()
        logger.info("Created test event %s", created.get("id"))
        return created
    except Exception:
        logger.exception("Failed to create test event")
        return None


__all__ = [
    "SyncTokenExpired",
    "load_credentials",
    "get_calendar_service",
    "fetch_upcoming_events",
    "list_upcoming_events",
    "sync_to_mongodb",
    "create_test_event",
]
