import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from config import Config
from mongo_service import get_collection

LOG_PATH = Path("logs")
LOG_PATH.mkdir(exist_ok=True)
logger = logging.getLogger(__name__)
handler = logging.FileHandler(LOG_PATH / "calendar_sync.log")
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

TOKEN_PATH = Path("token/token.json")


def load_credentials() -> Optional[Credentials]:
    """Load stored credentials from JSON and refresh if needed."""
    if not TOKEN_PATH.exists():
        logger.warning("No Google credentials found")
        return None
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, Config.GOOGLE_CALENDAR_SCOPES)
    if creds.expired and creds.refresh_token:
        logger.info("Refreshing Google credentials")
        creds.refresh(Request())
        TOKEN_PATH.write_text(creds.to_json())
    return creds


def get_calendar_service():
    """Return Google Calendar API service or ``None`` if credentials missing."""
    creds = load_credentials()
    if not creds:
        return None
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


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
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt


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
    while True:
        if page_token:
            params["pageToken"] = page_token
        result = service.events().list(**params).execute()
        events.extend(result.get("items", []))
        page_token = result.get("nextPageToken")
        if not page_token:
            break
    return events


def _build_doc(event: dict) -> dict:
    start_dt = _parse_datetime(event.get("start"))
    end_dt = _parse_datetime(event.get("end"))
    event_time = start_dt
    doc = {
        "google_event_id": event.get("id"),
        "title": event.get("summary", "No Title"),
        "description": event.get("description"),
        "location": event.get("location"),
        "updated": event.get("updated"),
        "start": start_dt,
        "end": end_dt,
        "event_time": event_time,
        "source": "google",
        "status": event.get("status"),
    }
    if event_time:
        doc["event_time"] = event_time
    return doc


def sync_to_mongodb(collection: str = "calendar_events") -> int:
    """Fetch events and upsert them into MongoDB."""
    service = get_calendar_service()
    if not service:
        return 0
    events = fetch_upcoming_events(service)
    if not events:
        return 0
    col = get_collection(collection)
    count = 0
    for ev in events:
        doc = _build_doc(ev)
        if not doc["google_event_id"]:
            continue
        col.update_one({"google_event_id": doc["google_event_id"]}, {"$set": doc}, upsert=True)
        count += 1
    logger.info("Synced %s events to MongoDB", count)
    return count


def create_test_event(
    summary: str = "✅ Bot verbunden", *, minutes_from_now: int = 5
) -> Optional[dict]:
    """Create a small test event in the primary calendar."""
    service = get_calendar_service()
    if not service:
        return None
    start = datetime.utcnow() + timedelta(minutes=minutes_from_now)
    end = start + timedelta(minutes=15)
    event = {
        "summary": summary,
        "start": {"dateTime": start.isoformat() + "Z"},
        "end": {"dateTime": end.isoformat() + "Z"},
    }
    created = service.events().insert(calendarId="primary", body=event).execute()
    logger.info("Created test event %s", created.get("id"))
    return created
