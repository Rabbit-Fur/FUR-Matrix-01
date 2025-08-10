"""Lightweight Google Calendar helpers.

This module provides a minimal wrapper around the Google Calendar API. All
MongoDB persistence, CRUD helpers and token storage logic have been removed in
favor of simple in-memory operations. Only the functions ``get_service`` and
``list_upcoming_events`` are exposed for external use. Additionally,
``format_event`` is offered as a convenience helper to create textual summaries
from raw event dictionaries.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from utils.time_utils import parse_calendar_datetime
from pymongo import UpdateOne

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
LOG_PATH = Path("logs")
logger = logging.getLogger(__name__)
_logging_initialized = False


def init_logging() -> None:
    """Initialize a file handler for this module's logger once."""

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


# ---------------------------------------------------------------------------
# Credential loading
# ---------------------------------------------------------------------------
_warned_once = False


def _default_token_path() -> Path:
    """Return the default path for stored OAuth tokens."""

    return Path(
        os.getenv("GOOGLE_TOKEN_STORAGE_PATH")
        or os.getenv("GOOGLE_CREDENTIALS_FILE")
        or "/data/google_token.json"
    )


@dataclass
class CalendarSettings:
    """Runtime configuration for Google Calendar access."""

    token_path: Path = field(default_factory=_default_token_path)
    calendar_id: str | None = os.getenv("GOOGLE_CALENDAR_ID")
    scopes: list[str] = field(
        default_factory=lambda: ["https://www.googleapis.com/auth/calendar.readonly"]
    )


class SyncTokenExpired(Exception):
    """Raised when stored OAuth credentials are missing or invalid."""


def load_credentials(settings: CalendarSettings | None = None) -> Credentials:
    """Load stored OAuth credentials from disk.

    The token file is expected to contain a refresh token. When the access token
    is expired it will be refreshed automatically and the new credentials are
    written back to the same file.

    Parameters
    ----------
    settings:
        Optional :class:`CalendarSettings` providing ``token_path`` and
        ``scopes``. When omitted, environment defaults are used.

    Raises
    ------
    SyncTokenExpired
        If the token file is absent, malformed or cannot be loaded by
        :func:`Credentials.from_authorized_user_file`.
    """

    global _warned_once
    settings = settings or CalendarSettings()
    token_path = settings.token_path
    setup_hint = (
        "Run services/google/oauth_setup.py and set "
        "GOOGLE_TOKEN_STORAGE_PATH or GOOGLE_CREDENTIALS_FILE."
    )
    if not token_path.exists():
        if not _warned_once:
            logger.warning(
                "No Google credentials found at %s. %s",
                token_path,
                setup_hint,
            )
            _warned_once = True
        raise SyncTokenExpired(
            f"No Google credentials found at {token_path}. {setup_hint}"
        ) from None
    try:
        info = json.loads(token_path.read_text())
    except Exception:  # noqa: BLE001
        logger.exception("Failed to read credentials JSON. %s", setup_hint)
        raise SyncTokenExpired(
            f"Failed to read credentials JSON at {token_path}. {setup_hint}"
        ) from None

    required = {"client_id", "client_secret", "refresh_token"}
    keys = set(info)
    if not required.issubset(keys):
        if ("installed" in info or "web" in info) and not _warned_once:
            logger.warning(
                "Credentials file %s looks like an OAuth client config, not a saved token. %s",
                token_path,
                setup_hint,
            )
            _warned_once = True
        elif not _warned_once:
            missing = ", ".join(sorted(required - keys))
            logger.warning(
                "Credentials file %s missing required keys: %s. %s",
                token_path,
                missing,
                setup_hint,
            )
            _warned_once = True
        raise SyncTokenExpired(
            f"Credentials file {token_path} missing required keys. {setup_hint}"
        ) from None

    scopes = settings.scopes
    try:
        creds = Credentials.from_authorized_user_info(info, scopes)
        if creds.expired and creds.refresh_token:
            logger.info("Refreshing Google credentials")
            creds.refresh(Request())
            token_path.write_text(creds.to_json())
        _warned_once = False
        return creds
    except Exception:  # noqa: BLE001
        logger.exception("Failed to load or refresh credentials. %s", setup_hint)
        raise SyncTokenExpired(
            f"Failed to load or refresh credentials from {token_path}. {setup_hint}"
        ) from None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
_service_cache: dict[Path, Any] = {}


def get_service(settings: CalendarSettings | None = None) -> Any | None:
    """Return a cached Google Calendar API service instance.

    Parameters
    ----------
    settings:
        Optional :class:`CalendarSettings` providing token location and scopes.

    The client is constructed on first use for the given ``token_path``. Missing
    or invalid credentials raise :class:`SyncTokenExpired` while other build
    errors return ``None``.
    """

    settings = settings or CalendarSettings()
    token_path = settings.token_path
    setup_hint = "Run services/google/oauth_setup.py to create tokens."
    if not token_path.exists():
        logger.warning("Google credentials not found at %s. %s", token_path, setup_hint)
        raise SyncTokenExpired(f"Google credentials not found at {token_path}. {setup_hint}")
    if token_path in _service_cache:
        return _service_cache[token_path]
    creds = load_credentials(settings)
    try:
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to build Google Calendar service")
        service = None
    _service_cache[token_path] = service
    return service


def list_upcoming_events(
    service: Any | None = None,
    *,
    calendar_id: Optional[str] = None,
    time_min: Optional[datetime] = None,
    time_max: Optional[datetime] = None,
    max_results: int = 2500,
    settings: CalendarSettings | None = None,
) -> list[dict]:
    """Return upcoming events from Google Calendar.

    Parameters
    ----------
    service:
        Existing calendar service instance. When ``None`` a new service is
        created via :func:`get_service` using ``settings``.
    calendar_id:
        Specific calendar to query. Defaults to ``settings.calendar_id``.
    time_min / time_max:
        Optional datetime boundaries. Values are converted to UTC as required by
        the API.
    max_results:
        Maximum number of events to fetch.
    settings:
        Optional :class:`CalendarSettings` object providing defaults.
    """

    settings = settings or CalendarSettings()
    service = service or get_service(settings)
    if not service:
        return []
    calendar_id = calendar_id or settings.calendar_id
    if not calendar_id:
        logger.warning("GOOGLE_CALENDAR_ID not configured")
        return []

    params: dict[str, Any] = {
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
    page_token: str | None = None
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


def format_event(event: dict) -> str:
    """Return a human-readable summary for an event dictionary."""

    start = parse_calendar_datetime(event.get("start"))
    title = event.get("summary", "No Title")
    if start:
        return f"{start.strftime('%Y-%m-%d %H:%M')} - {title}"
    return title


def sync_to_mongodb(
    mongo_db,
    collection_name: str = "calendar_events",
    max_results: int = 250,
    time_min: Optional[datetime] = None,
    time_max: Optional[datetime] = None,
    settings: CalendarSettings | None = None,
) -> int:
    """Fetch events via :class:`CalendarService` and upsert them into MongoDB."""

    from services.calendar_service import (
        CalendarService,
        SyncTokenExpired as ServiceSyncTokenExpired,
    )

    settings = settings or CalendarSettings()
    svc = CalendarService(
        calendar_id=settings.calendar_id,
        token_path=str(settings.token_path),
        scopes=settings.scopes,
    )
    if time_min is None:
        time_min = datetime.now(timezone.utc)

    try:
        events = svc.list_upcoming_events(
            max_results=max_results,
            time_min=time_min,
            time_max=time_max,
            single_events=True,
            order_by="startTime",
        )
    except ServiceSyncTokenExpired as err:
        logger.warning("Google token problem: %s", err)
        return 0

    if not events:
        return 0

    cal_id = settings.calendar_id
    ops = []
    for e in events:
        e["__calendar_id"] = cal_id
        ops.append(UpdateOne({"id": e.get("id")}, {"$set": e}, upsert=True))

    if not ops:
        return 0

    res = mongo_db[collection_name].bulk_write(ops, ordered=False)
    changed = (res.upserted_count or 0) + (res.modified_count or 0)
    return int(changed)


__all__ = [
    "CalendarSettings",
    "get_service",
    "list_upcoming_events",
    "format_event",
    "sync_to_mongodb",
    "load_credentials",
    "SyncTokenExpired",
]
