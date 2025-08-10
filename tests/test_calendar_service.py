from datetime import datetime, timedelta, timezone

import pytest

from services.calendar_service import CalendarService


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
