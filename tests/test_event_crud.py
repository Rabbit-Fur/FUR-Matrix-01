import asyncio

import mongomock
import pytest

from crud import event_crud
from schemas.event_schema import EventModel


@pytest.fixture(autouse=True)
def _mock_db(monkeypatch):
    client = mongomock.MongoClient()
    db = client["testdb"]
    monkeypatch.setattr(event_crud, "db", db)
    monkeypatch.setattr(event_crud, "collection", db[event_crud.COLLECTION_NAME])
    yield


@pytest.mark.asyncio
async def test_create_and_fetch_by_id():
    ev = EventModel(title="Ping", date="2025-01-01T00:00:00")
    created = await event_crud.create_event(ev)
    assert created.id
    fetched = await event_crud.get_event_by_id(created.id)
    assert fetched and fetched.title == "Ping"


@pytest.mark.asyncio
async def test_get_and_delete_by_guild():
    col = event_crud.collection
    await asyncio.to_thread(
        col.insert_one,
        {
            "title": "T",
            "date": "2025-01-01T00:00:00",
            "guild_id": "1",
        },
    )
    events = await event_crud.get_events_by_guild("1")
    assert len(events) == 1
    deleted = await event_crud.delete_event_by_id(events[0].id)
    assert deleted == 1
