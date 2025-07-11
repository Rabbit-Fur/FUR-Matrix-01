from datetime import timezone

import logging
import google_calendar_sync as mod


class DummyCollection:
    def __init__(self):
        self.docs = {}

    def update_one(self, flt, update, upsert=False):
        self.docs[flt["google_id"]] = update["$set"]


def test_sync_to_mongodb(monkeypatch):
    dummy = DummyCollection()

    def fake_fetch(*a, **k):
        return [
            {
                "id": "g1",
                "summary": "Test",
                "start": {"dateTime": "2025-01-01T10:00:00Z"},
                "end": {"dateTime": "2025-01-01T11:00:00Z"},
                "updated": "2025-01-01T09:00:00Z",
            }
        ]

    monkeypatch.setattr(mod, "fetch_upcoming_events", fake_fetch)
    monkeypatch.setattr(mod, "get_calendar_service", lambda: object())
    monkeypatch.setattr(mod, "get_collection", lambda name: dummy)

    count = mod.sync_to_mongodb("events")
    assert count == 1
    doc = dummy.docs["g1"]
    assert doc["title"] == "Test"
    assert doc["start"].hour == 10
    assert doc["end"].hour == 11
    assert doc["event_time"].tzinfo == timezone.utc


def test_all_day_event(monkeypatch):
    dummy = DummyCollection()

    events = [
        {
            "id": "g2",
            "summary": "All Day",
            "start": {"date": "2025-01-02"},
            "end": {"date": "2025-01-03"},
            "updated": "2025-01-01T11:00:00Z",
        }
    ]

    monkeypatch.setattr(mod, "fetch_upcoming_events", lambda *a, **k: events)
    monkeypatch.setattr(mod, "get_calendar_service", lambda: object())
    monkeypatch.setattr(mod, "get_collection", lambda name: dummy)

    mod.sync_to_mongodb("events")
    doc = dummy.docs["g2"]
    assert doc["event_time"].hour == 0
    assert doc["event_time"].tzinfo == timezone.utc


def test_load_credentials_warns_once(monkeypatch, tmp_path, caplog):
    missing = tmp_path / "token.json"
    monkeypatch.setattr(mod, "TOKEN_PATH", missing, raising=False)
    mod._warned_once = False
    with caplog.at_level(logging.WARNING):
        assert mod.load_credentials() is None
    assert "No Google credentials found" in caplog.text
    caplog.clear()
    with caplog.at_level(logging.WARNING):
        assert mod.load_credentials() is None
    assert caplog.text == ""
