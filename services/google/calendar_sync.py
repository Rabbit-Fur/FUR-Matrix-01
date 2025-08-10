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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from config import Config
from utils.time_utils import parse_calendar_datetime

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
TOKEN_PATH = Path(os.getenv("GOOGLE_CREDENTIALS_FILE", "/data/google_token.json"))
_warned_once = False


def load_credentials() -> Optional[Credentials]:
    """Load stored OAuth credentials from disk.

    The token file is expected to contain a refresh token. When the access token
    is expired it will be refreshed automatically and the new credentials are
    written back to the same file.
    """

    global _warned_once
    if not TOKEN_PATH.exists():
        if not _warned_once:
            logger.warning("No Google credentials found at %s", TOKEN_PATH)
            _warned_once = True
        return None
    try:
        info = json.loads(TOKEN_PATH.read_text())
    except Exception:  # noqa: BLE001
        logger.exception("Failed to read credentials JSON")
        return None

    required = {"client_id", "client_secret", "refresh_token"}
    keys = set(info)
    if not required.issubset(keys):
        if ("installed" in info or "web" in info) and not _warned_once:
            logger.warning(
                "Credentials file %s looks like an OAuth client config, not a saved token",
                TOKEN_PATH,
            )
            _warned_once = True
        elif not _warned_once:
            missing = ", ".join(sorted(required - keys))
            logger.warning("Credentials file %s missing required keys: %s", TOKEN_PATH, missing)
            _warned_once = True
        return None

    try:
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, Config.GOOGLE_CALENDAR_SCOPES)
        if creds.expired and creds.refresh_token:
            logger.info("Refreshing Google credentials")
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
        _warned_once = False
        return creds
    except Exception:  # noqa: BLE001
        logger.exception("Failed to load or refresh credentials")
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def get_service() -> Any | None:
    """Return a Google Calendar API service instance.

    ``None`` is returned when credentials are missing or building the service
    fails.
    """

    creds = load_credentials()
    if not creds:
        return None
    try:
        return build("calendar", "v3", credentials=creds, cache_discovery=False)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to build Google Calendar service")
        return None


def list_upcoming_events(
    service: Any | None = None,
    *,
    calendar_id: Optional[str] = None,
    time_min: Optional[datetime] = None,
    time_max: Optional[datetime] = None,
    max_results: int = 2500,
) -> list[dict]:
    """Return upcoming events from Google Calendar.

    Parameters
    ----------
    service:
        Existing calendar service instance. When ``None`` a new service is
        created via :func:`get_service`.
    calendar_id:
        Specific calendar to query. Defaults to ``Config.GOOGLE_CALENDAR_ID``.
    time_min / time_max:
        Optional datetime boundaries. Values are converted to UTC as required by
        the API.
    max_results:
        Maximum number of events to fetch.
    """

    service = service or get_service()
    if not service:
        return []
    calendar_id = calendar_id or Config.GOOGLE_CALENDAR_ID
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


__all__ = ["get_service", "list_upcoming_events", "format_event", "load_credentials"]
