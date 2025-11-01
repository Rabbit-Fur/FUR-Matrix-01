from datetime import datetime, timedelta, timezone

import pytest

from crud import event_crud
from schemas.event_schema import EventModel
from services.calendar_service import CalendarService


class InMemoryCollection:
    def __init__(self):
        self.data = {}

    async def find_one(self, query):
        return self.data.get(query.get("_id"))

    async def update_one(self, query, update, upsert=False):  # noqa: D401
        if upsert or query.get("_id") in self.data:
            key = query.get("_id")
            if key is None:
                key = "google"
            doc = self.data.get(key, {})
            doc.update(update.get("$set", {}))
            self.data[key] = doc
        return {"acknowledged": True}


class DummyCollection:
    database = {}


@pytest.mark.asyncio
async def test_list_upcoming_events_uses_params(monkeypatch):
    service = CalendarService(
        events_collection=DummyCollection(), tokens_collection=DummyCollection()
    )

    called = {}

    async def fake_get_range(self, start, end):  # noqa: D401
        called["start"] = start
        called["end"] = end
        return [{"id": 1}, {"id": 2}, {"id": 3}]

    monkeypatch.setattr(CalendarService, "_get_range", fake_get_range, raising=False)

    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end = datetime(2024, 1, 2, tzinfo=timezone.utc)
    events = await service.list_upcoming_events(start=start, end=end, max_results=2)

    assert called["start"] == start
    assert called["end"] == end
    assert len(events) == 2


@pytest.mark.asyncio
async def test_list_upcoming_events_defaults(monkeypatch):
    service = CalendarService(
        events_collection=DummyCollection(), tokens_collection=DummyCollection()
    )

    called = {}

    async def fake_get_range(self, start, end):  # noqa: D401
        called["start"] = start
        called["end"] = end
        return []

    monkeypatch.setattr(CalendarService, "_get_range", fake_get_range, raising=False)

    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    await service.list_upcoming_events()

    assert timedelta(minutes=9) < called["start"] - now < timedelta(minutes=11)
    assert called["end"] - called["start"] == timedelta(minutes=1)


@pytest.mark.asyncio
async def test_sync_and_range_query_includes_date(monkeypatch):
    tokens_collection = InMemoryCollection()
    service = CalendarService(events_collection=DummyCollection(), tokens_collection=tokens_collection)

    stored_docs: dict[str, dict] = {}

    async def fake_upsert_event(data, *, col):  # noqa: D401
        stored_docs[data["google_id"]] = data

    async def fake_get_events_in_range(start, end, *, col):  # noqa: D401
        results = []
        for doc in stored_docs.values():
            event_time = doc.get("event_time")
            if event_time is None or (start <= event_time < end):
                results.append(EventModel(**doc))
        return results

    def fake_build_service(self):  # noqa: D401
        self.service = object()

    async def fake_api_list(self, params):  # noqa: D401
        start_time = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
        return {
            "items": [
                {
                    "id": "event-1",
                    "summary": "Kickoff",
                    "start": {"dateTime": start_time.isoformat().replace("+00:00", "Z")},
                    "end": {
                        "dateTime": (start_time + timedelta(hours=1)).isoformat().replace("+00:00", "Z")
                    },
                    "status": "confirmed",
                    "updated": "2024-12-31T00:00:00+00:00",
                }
            ],
            "nextSyncToken": "token-1",
        }

    monkeypatch.setattr(event_crud, "upsert_event", fake_upsert_event)
    monkeypatch.setattr(event_crud, "get_events_in_range", fake_get_events_in_range)
    monkeypatch.setattr(CalendarService, "_build_service", fake_build_service, raising=False)
    monkeypatch.setattr(CalendarService, "_api_list", fake_api_list, raising=False)

    count = await service.sync()
    assert count == 1

    stored_doc = stored_docs["event-1"]
    assert stored_doc["date"].startswith("2025-01-01T12:00:00")

    window_start = datetime(2025, 1, 1, 11, 59, tzinfo=timezone.utc)
    window_end = datetime(2025, 1, 1, 12, 1, tzinfo=timezone.utc)
    events = await service._get_range(window_start, window_end)

    assert events
    assert events[0]["date"] == stored_doc["date"]
