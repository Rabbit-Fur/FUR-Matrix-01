from datetime import datetime
from zoneinfo import ZoneInfo

import utils.timezone as mod


def test_get_timezone_valid():
    tz = mod.get_timezone("Europe/Berlin")
    assert isinstance(tz, ZoneInfo)
    assert tz.key == "Europe/Berlin"


def test_get_timezone_invalid_defaults():
    tz = mod.get_timezone("Invalid/Zone")
    assert tz == mod.DEFAULT_TZ


def test_convert_datetime():
    dt = datetime(2025, 1, 1, 12, 0)
    converted = mod.convert_datetime(dt, "America/New_York")
    assert converted.tzinfo.key == "America/New_York"
    assert converted.hour == 7


def test_get_user_timezone_dict():
    tz = mod.get_user_timezone({"timezone": "Asia/Tokyo"})
    assert tz.key == "Asia/Tokyo"
