import mongo_service
import utils.google_sync as mod


def test_import_events_upserts():
    col = mongo_service.db["events"]
    col.delete_many({})

    events = [
        {
            "id": "g1",
            "summary": "Test",
            "description": "foo",
            "location": "bar",
            "start": {"dateTime": "2025-01-01T10:00:00Z"},
            "end": {"dateTime": "2025-01-01T11:00:00Z"},
            "updated": "2025-01-01T09:00:00Z",
        }
    ]
    mod.import_events(events)
    assert col.count_documents({"google_event_id": "g1"}) == 1

    events2 = [
        {
            "id": "g1",
            "summary": "Test2",
            "description": "baz",
            "location": "qux",
            "start": {"dateTime": "2025-01-01T12:00:00Z"},
            "end": {"dateTime": "2025-01-01T13:00:00Z"},
            "updated": "2025-01-02T09:00:00Z",
        }
    ]
    mod.import_events(events2)
    doc = col.find_one({"google_event_id": "g1"})
    assert doc["title"] == "Test2"
    assert doc["start"].hour == 12
    assert doc["end"].hour == 13
    assert doc["description"] == "baz"
    assert doc["location"] == "qux"
    assert doc["source"] == "google"


def test_sync_google_calendar(monkeypatch):
    called = {}

    def fake_fetch(service, calendar_id):
        called["calendar_id"] = calendar_id
        return [
            {
                "id": "g2",
                "summary": "Meet",
                "start": {"date": "2025-01-02"},
                "updated": "2025-01-01T11:00:00Z",
            }
        ]

    def fake_import(events):
        called["imported"] = events

    monkeypatch.setattr(mod, "get_service", lambda: object())
    monkeypatch.setattr(mod, "fetch_calendar_events", fake_fetch)
    monkeypatch.setattr(mod, "import_events", fake_import)
    monkeypatch.setattr(mod.Config, "GOOGLE_CALENDAR_ID", "test")

    mod.sync_google_calendar()
    assert called["calendar_id"] == "test"
    assert called["imported"][0]["id"] == "g2"
