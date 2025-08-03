from __future__ import annotations

from datetime import date as date_type
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from babel.dates import format_datetime

from fur_lang import i18n
from mongo_service import get_collection


def parse_event_time(value: Any) -> datetime | None:
    """Return ``datetime`` for event_time field or ``None`` if invalid."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return None


def get_events_for(dt: datetime | date_type, tz: str | ZoneInfo = "Europe/Berlin") -> list[dict]:
    """Return all events for the given day in ``tz`` sorted by ``event_time``."""
    # Fix: Compare event dates in Europe/Berlin instead of UTC to avoid off-by-one errors
    tzinfo = ZoneInfo(tz) if isinstance(tz, str) else tz

    if isinstance(dt, datetime):
        day = dt.astimezone(tzinfo).date()
    else:
        day = dt

    start_local = datetime.combine(day, datetime.min.time(), tzinfo)
    end_local = start_local + timedelta(days=1)
    start = start_local.astimezone(timezone.utc)
    end = end_local.astimezone(timezone.utc)

    events = (
        get_collection("events")
        .find({"event_time": {"$gte": start, "$lt": end}})
        .sort("event_time", 1)
    )
    return list(events)


def format_events(events: Iterable[dict]) -> str:
    """Return a newline separated bullet list for the given events."""
    lines = []
    lang = i18n.current_lang()
    tz_prefix = i18n.t("prefix_utc", default="UTC", lang=lang)
    for ev in events:
        dt = parse_event_time(ev.get("event_time"))
        if not dt:
            continue
        title = ev.get("title", "Event")
        dt_text = format_datetime(dt, "dd.MM.yyyy HH:mm", locale=lang)
        lines.append(f"- {title} – {dt_text} {tz_prefix}")
    return "\n".join(lines)
