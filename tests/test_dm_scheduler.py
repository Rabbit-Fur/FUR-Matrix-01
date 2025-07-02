import types
from datetime import datetime, timedelta

import pytest


@pytest.mark.asyncio
async def test_send_daily_dm(monkeypatch):
    from bot import dm_scheduler as mod

    called = {}
    monkeypatch.setattr(mod, "get_dm_users", lambda: [1])

    async def fake_send(user, msg):
        called[user] = msg

    monkeypatch.setattr(mod, "send_dm", fake_send)

    async def fetch_user(uid):
        return uid

    fake_bot = types.SimpleNamespace(fetch_user=fetch_user)

    await mod.send_daily_dm(fake_bot)

    assert called.get(1) == "Good morning! Your events for today are ready."


@pytest.mark.asyncio
async def test_check_upcoming_events(monkeypatch):
    from bot import dm_scheduler as mod

    now = datetime.utcnow()
    events = [{"_id": 1, "start": now + timedelta(minutes=5), "user_id": 1, "title": "Ping"}]

    class FakeCollection:
        def find(self, query):
            return events

        def update_one(self, q, u):
            events[0]["dm_warning_sent"] = True

    monkeypatch.setattr(mod, "get_collection", lambda name: FakeCollection())
    sent = {}

    async def fake_send_dm(user, text):
        sent[user] = text

    monkeypatch.setattr(mod, "send_dm", fake_send_dm)

    async def fetch_user(uid):
        return uid

    fake_bot = types.SimpleNamespace(fetch_user=fetch_user)

    await mod.check_upcoming_events(fake_bot)

    assert sent.get(1)
    assert events[0]["dm_warning_sent"]


def test_schedule_dm_tasks(monkeypatch):
    from bot import dm_scheduler as mod

    jobs = []

    class FakeScheduler:
        running = False

        def add_job(self, func, trigger, **kw):
            jobs.append((func, trigger))

        def start(self):
            self.running = True

    fake = FakeScheduler()
    monkeypatch.setattr(mod, "scheduler", fake)

    mod.schedule_dm_tasks("bot")

    assert fake.running
    assert len(jobs) == 2
