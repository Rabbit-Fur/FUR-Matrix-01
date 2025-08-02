from datetime import datetime, timezone

from utils.time_utils import parse_calendar_datetime


def test_parse_calendar_datetime_with_datetime():
    info = {"dateTime": "2025-01-01T12:00:00-05:00"}
    parsed = parse_calendar_datetime(info)
    assert parsed == datetime(2025, 1, 1, 17, 0, tzinfo=timezone.utc)


def test_parse_calendar_datetime_with_date():
    info = {"date": "2025-01-01"}
    parsed = parse_calendar_datetime(info)
    assert parsed == datetime(2025, 1, 1, tzinfo=timezone.utc)
