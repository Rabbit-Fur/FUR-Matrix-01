from __future__ import annotations

from datetime import date as date_type
from datetime import datetime, timedelta
from typing import Any, Iterable

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


def get_events_for(dt: datetime | date_type) -> list[dict]:
    """Return all events for the given day sorted by ``event_time``."""
    if isinstance(dt, datetime):
        day = dt.date()
    else:
        day = dt
    start = datetime.combine(day, datetime.min.time())
    end = start + timedelta(days=1)
    events = (
        get_collection("events")
        .find({"event_time": {"$gte": start, "$lt": end}})
        .sort("event_time", 1)
    )
    return list(events)


def format_events(events: Iterable[dict]) -> str:
    """Return a newline separated bullet list for the given events."""
    lines = []
    for ev in events:
        dt = parse_event_time(ev.get("event_time"))
        if not dt:
            continue
        title = ev.get("title", "Event")
        lines.append(f"- {title} – {dt.strftime('%d.%m.%Y %H:%M')} UTC")
    return "\n".join(lines)
