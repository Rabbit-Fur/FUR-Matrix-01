import os
from dataclasses import dataclass, field
from typing import List, Optional

DEFAULT_TOKEN_PATH = "/data/google_token.json"
DEFAULT_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


@dataclass
class GoogleCalendarSettings:
    """Environment driven configuration for Google Calendar access."""

    calendar_id: Optional[str]
    token_path: str = DEFAULT_TOKEN_PATH
    credentials_file: str = DEFAULT_TOKEN_PATH
    scopes: List[str] = field(default_factory=lambda: DEFAULT_SCOPES.copy())


def get_google_calendar_settings() -> GoogleCalendarSettings:
    """Retrieve Google Calendar configuration from environment variables.

    Returns a :class:`GoogleCalendarSettings` instance with sensible defaults.
    ``GOOGLE_TOKEN_STORAGE_PATH`` falls back to ``GOOGLE_CREDENTIALS_FILE``
    which itself defaults to ``/data/google_token.json``.
    ``GOOGLE_CALENDAR_SCOPES`` is parsed as a comma separated list.
    """

    credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE", DEFAULT_TOKEN_PATH)
    token_path = os.getenv("GOOGLE_TOKEN_STORAGE_PATH", credentials_file)
    scopes_env = os.getenv("GOOGLE_CALENDAR_SCOPES", ",".join(DEFAULT_SCOPES))
    scopes = [s.strip() for s in scopes_env.split(",") if s.strip()]
    return GoogleCalendarSettings(
        calendar_id=os.getenv("GOOGLE_CALENDAR_ID"),
        token_path=token_path,
        credentials_file=credentials_file,
        scopes=scopes,
    )
