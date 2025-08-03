import types

import pytest

import services.calendar_service as mod
from datetime import datetime, timedelta, timezone


class DummyCollection:
    def __init__(self):
        self.docs = []

    async def find_one(self, filt):
        for doc in self.docs:
            if all(doc.get(k) == v for k, v in filt.items()):
                return doc
        return None

    async def update_one(self, flt, update, upsert=False):
        for doc in self.docs:
            if all(doc.get(k) == v for k, v in flt.items()):
                doc.update(update["$set"])
                return
        self.docs.append({**flt, **update["$set"]})

    def find(self, query):
        self._query = query
        return self

    def sort(self, key, direction):
        self.docs.sort(key=lambda d: d.get(key))
        return self

    async def to_list(self, length=None):
        start = self._query["event_time"]["$gte"]
        end = self._query["event_time"]["$lt"]
        result = [d for d in self.docs if start <= d["event_time"] < end]
        return result


@pytest.mark.asyncio
async def test_sync_stores_events_and_token(monkeypatch):
    events_col = DummyCollection()
    tokens_col = DummyCollection()
    service = mod.CalendarService(
        calendar_id="c1", events_collection=events_col, tokens_collection=tokens_col
    )
    monkeypatch.setattr(service, "_build_service", lambda: setattr(service, "service", object()))

    async def fake_api(params):
        return {
            "items": [
                {
                    "id": "g1",
                    "summary": "Test",
                    "start": {"dateTime": "2025-01-01T10:00:00Z"},
                }
            ],
            "nextSyncToken": "tok",
        }

    monkeypatch.setattr(service, "_api_list", fake_api)

    count = await service.sync()
    assert count == 1
    assert events_col.docs[0]["google_id"] == "g1"
    token = await tokens_col.find_one({"_id": "google"})
    assert token["token"] == "tok"


@pytest.mark.asyncio
async def test_sync_resync_on_410(monkeypatch):
    events_col = DummyCollection()
    tokens_col = DummyCollection()
    service = mod.CalendarService(
        calendar_id="c1", events_collection=events_col, tokens_collection=tokens_col
    )
    monkeypatch.setattr(service, "_build_service", lambda: setattr(service, "service", object()))

    calls = {"n": 0}

    async def fake_api(params):
        calls["n"] += 1
        if calls["n"] == 1:
            resp = types.SimpleNamespace(status=410, reason="Gone")
            raise mod.HttpError(resp, b"gone")
        return {"items": [], "nextSyncToken": "tok2"}

    monkeypatch.setattr(service, "_api_list", fake_api)

    count = await service.sync()
    assert calls["n"] == 2
    token = await tokens_col.find_one({"_id": "google"})
    assert token["token"] == "tok2"
    assert count == 0


@pytest.mark.asyncio
async def test_sync_uses_stored_token(monkeypatch):
    events_col = DummyCollection()
    tokens_col = DummyCollection()
    tokens_col.docs.append({"_id": "google", "token": "old"})
    service = mod.CalendarService(
        calendar_id="c1", events_collection=events_col, tokens_collection=tokens_col
    )
    monkeypatch.setattr(service, "_build_service", lambda: setattr(service, "service", object()))

    captured = {}

    async def fake_api(params):
        captured.update(params)
        return {"items": [], "nextSyncToken": "new"}

    monkeypatch.setattr(service, "_api_list", fake_api)

    count = await service.sync()
    assert count == 0
    assert captured.get("syncToken") == "old"
    token = await tokens_col.find_one({"_id": "google"})
    assert token["token"] == "new"


@pytest.mark.asyncio
async def test_get_next_event_and_events_for_date(monkeypatch):
    events_col = DummyCollection()
    tokens_col = DummyCollection()
    service = mod.CalendarService(events_collection=events_col, tokens_collection=tokens_col)

    async def fake_get_range(start, end, *, col=None):
        col = col or events_col
        result = [d for d in col.docs if start <= d["event_time"] < end]
        result.sort(key=lambda d: d["event_time"])
        return result

    monkeypatch.setattr(mod.event_crud, "get_events_in_range", fake_get_range)

    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    events_col.docs.extend(
        [
            {"event_time": now + timedelta(hours=1), "title": "A"},
            {"event_time": now + timedelta(days=1), "title": "B"},
        ]
    )

    ev = await service.get_next_event()
    assert ev and ev["title"] == "A"

    events = await service.get_events_for_date((now + timedelta(hours=1)).date())
    assert len(events) == 1 and events[0]["title"] == "A"
