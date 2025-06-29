from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

DEFAULT_TZ = ZoneInfo("UTC")


def get_timezone(name: str | None) -> ZoneInfo:
    """Return ZoneInfo for *name* or ``DEFAULT_TZ`` when invalid."""
    if not name:
        return DEFAULT_TZ
    try:
        return ZoneInfo(name)
    except Exception:
        return DEFAULT_TZ


def get_user_timezone(user: Any) -> ZoneInfo:
    """Return timezone for user object or mapping."""
    if not user:
        return DEFAULT_TZ
    if isinstance(user, dict):
        name = user.get("timezone")
    else:
        name = getattr(user, "timezone", None)
    return get_timezone(name)


def convert_datetime(dt: datetime, tz: str | ZoneInfo | None) -> datetime:
    """Convert *dt* to timezone ``tz`` (defaults to UTC)."""
    if isinstance(tz, str) or tz is None:
        tz = get_timezone(tz)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz)
