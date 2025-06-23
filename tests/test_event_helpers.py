from datetime import datetime

import utils.event_helpers as mod


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
            {"title": "A", "event_time": datetime(2025, 1, 1, 10, 0)},
            {"title": "B", "event_time": datetime(2025, 1, 2, 12, 0)},
        ]
    )


def test_get_events_for(monkeypatch):
    monkeypatch.setattr(mod, "get_collection", fake_get_collection)
    events = mod.get_events_for(datetime(2025, 1, 1))
    assert len(events) == 1
    assert events[0]["title"] == "A"


def test_format_events():
    events = [
        {"title": "X", "event_time": datetime(2025, 1, 1, 8, 0)},
        {"title": "Y", "event_time": "2025-01-02T09:00:00"},
    ]
    text = mod.format_events(events)
    assert "- X" in text
    assert "01.01.2025" in text
    assert "02.01.2025" in text
