"""Utility helpers for working with calendar datetimes."""

from datetime import datetime, timezone
import logging

log = logging.getLogger(__name__)


def parse_calendar_datetime(info: dict | None) -> datetime | None:
    """Parse Google Calendar date or datetime dict into UTC ``datetime``.

    The Google Calendar API returns event start/end times either under the
    ``dateTime`` key for timed events or ``date`` for all-day events. This
    helper normalizes both formats to a timezone-aware UTC ``datetime``.

    Parameters
    ----------
    info:
        Mapping from the Calendar API containing either ``dateTime`` or
        ``date``.

    Returns
    -------
    datetime | None
        A timezone-aware UTC ``datetime`` instance or ``None`` when the
        input could not be parsed.
    """

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
        log.warning("Could not parse datetime: %s", value)
        return None


__all__ = ["parse_calendar_datetime"]
