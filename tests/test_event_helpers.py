from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import utils.event_helpers as mod

from fur_lang import i18n


class FakeEvents:
    def __init__(self, docs):
        self.docs = docs

    def find(self, query):
        self.query = query
        return self

    def sort(self, *_, **__):
        start = self.query["event_time"]["$gte"]
        end = self.query["event_time"]["$lt"]
        result = [d for d in self.docs if start <= d["event_time"] < end]
        return sorted(result, key=lambda d: d["event_time"])


def fake_get_collection(name):
    return FakeEvents(
        [
            {"title": "A", "event_time": datetime(2025, 1, 1, 22, 0, tzinfo=timezone.utc)},
            {"title": "B", "event_time": datetime(2025, 1, 2, 12, 0, tzinfo=timezone.utc)},
        ]
    )


def test_get_events_for(monkeypatch):
    monkeypatch.setattr(mod, "get_collection", fake_get_collection)
    tz = ZoneInfo("Europe/Berlin")
    events = mod.get_events_for(datetime(2025, 1, 1, 12, 0, tzinfo=tz))
    assert len(events) == 1
    assert events[0]["title"] == "A"


def test_get_events_for_tomorrow(monkeypatch):
    monkeypatch.setattr(mod, "get_collection", fake_get_collection)
    tz = ZoneInfo("Europe/Berlin")
    events = mod.get_events_for(datetime(2025, 1, 2, 12, 0, tzinfo=tz))
    assert len(events) == 1
    assert events[0]["title"] == "B"


def test_format_events(monkeypatch):
    events = [
        {"title": "X", "event_time": datetime(2025, 1, 1, 8, 0)},
        {"title": "Y", "event_time": "2025-01-02T09:00:00"},
    ]
    monkeypatch.setattr(i18n, "current_lang", lambda: "de")
    monkeypatch.setattr(
        i18n,
        "t",
        lambda key, default=None, lang=None, **kwargs: {"prefix_utc": "UTC"}.get(
            key,
            default or key,
        ),
    )
    text = mod.format_events(events)
    assert "- X" in text
    assert "01.01.2025" in text
    assert "02.01.2025" in text
    assert text.endswith("UTC")
