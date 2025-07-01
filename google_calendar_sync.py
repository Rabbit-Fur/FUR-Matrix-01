import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import Config
from mongo_service import get_collection

# Logging setup
LOG_PATH = Path("logs")
LOG_PATH.mkdir(exist_ok=True)
logger = logging.getLogger(__name__)
handler = logging.FileHandler(LOG_PATH / "calendar_sync.log")
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Token path
TOKEN_PATH = Path(os.getenv("GOOGLE_CREDENTIALS_FILE", "/data/google_token.json"))


def _get_token_collection():
    """Return the MongoDB collection used for sync tokens."""
    return get_collection("calendar_tokens")


def _load_sync_token() -> str | None:
    doc = _get_token_collection().find_one({"_id": "google"})
    return doc.get("token") if doc else None


def _store_sync_token(token: str) -> None:
    _get_token_collection().update_one({"_id": "google"}, {"$set": {"token": token}}, upsert=True)


def load_credentials() -> Optional[Credentials]:
    """Load stored credentials from JSON and refresh if needed."""
    if not TOKEN_PATH.exists():
        logger.warning("No Google credentials found at %s", TOKEN_PATH)
        return None
    try:
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, Config.GOOGLE_CALENDAR_SCOPES)
        if creds.expired and creds.refresh_token:
            logger.info("Refreshing Google credentials")
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
        return creds
    except Exception:  # noqa: BLE001
        logger.exception("Failed to load or refresh credentials")
        return None


def get_calendar_service():
    """Return Google Calendar API service or ``None`` if credentials missing."""
    creds = load_credentials()
    if not creds:
        return None
    try:
        return build("calendar", "v3", credentials=creds, cache_discovery=False)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to build Google Calendar service")
        return None


def _parse_datetime(info: Optional[dict]) -> Optional[datetime]:
    if not info:
        return None
    value = info.get("dateTime") or info.get("date")
    if not value:
        return None
    if value.endswith("Z"):
        value = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt
    except ValueError:
        logger.warning("Could not parse datetime: %s", value)
        return None


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
    if not service:
        return []
    calendar_id = calendar_id or Config.GOOGLE_CALENDAR_ID
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


def _build_doc(event: dict) -> dict:
    start_dt = _parse_datetime(event.get("start"))
    end_dt = _parse_datetime(event.get("end"))
    return {
        "google_event_id": event.get("id"),
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
    if not service:
        logger.warning("No calendar service – skipping sync")
        return 0
    calendar_id = Config.GOOGLE_CALENDAR_ID
    if not calendar_id:
        logger.warning("GOOGLE_CALENDAR_ID not configured")
        return 0
    token = _load_sync_token()
    params: dict[str, Any] = {
        "calendarId": calendar_id,
        "singleEvents": True,
        "showDeleted": True,
        "maxResults": 2500,
    }
    if token:
        params["syncToken"] = token
    else:
        params["timeMin"] = datetime.utcnow().isoformat() + "Z"
    try:
        data = service.events().list(**params).execute()
    except HttpError as exc:
        if exc.resp.status == 410:  # sync token expired
            logger.warning("Sync token expired; performing full sync")
            params.pop("syncToken", None)
            params["timeMin"] = datetime.utcnow().isoformat() + "Z"
            data = service.events().list(**params).execute()
        else:
            logger.exception("Calendar API error")
            return 0

    events = data.get("items", [])
    if not events:
        logger.info("No events returned from calendar")
        return 0

    col = get_collection(collection)
    count = 0
    for ev in events:
        doc = _build_doc(ev)
        if not doc["google_event_id"]:
            continue
        try:
            col.update_one({"google_event_id": doc["google_event_id"]}, {"$set": doc}, upsert=True)
            count += 1
        except Exception:
            logger.exception("Failed to sync event %s", doc.get("google_event_id"))
    new_token = data.get("nextSyncToken")
    if new_token:
        _store_sync_token(new_token)
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
