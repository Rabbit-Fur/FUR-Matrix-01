import types
from datetime import datetime, timedelta

import discord
from config import Config

import pytest


@pytest.mark.asyncio
async def test_send_daily_dm(monkeypatch):
    from bot import dm_scheduler as mod

    called = {}
    monkeypatch.setattr(mod, "get_dm_users", lambda: [1])

    async def fake_send(user, msg, dm_type):
        called["user"] = user
        called["msg"] = msg
        called["type"] = dm_type

    monkeypatch.setattr(mod, "send_embed_dm", fake_send)

    class FakeFlags:
        def __init__(self) -> None:
            self.updated = False

        def find_one(self, q):
            return None

        def update_one(self, q, u, upsert=False):
            self.updated = True

    flags = FakeFlags()

    class FakeSettings:
        def find_one(self, q):
            return {"value": "http://img"}

    def fake_get_collection(name):
        if name == "flags":
            return flags
        if name == "settings":
            return FakeSettings()
        return None

    monkeypatch.setattr(mod, "get_collection", fake_get_collection)

    async def fetch_user(uid):
        return uid

    fake_bot = types.SimpleNamespace(fetch_user=fetch_user)

    await mod.send_daily_dm(fake_bot)

    assert called["msg"] == "Good morning! Your events for today are ready."
    assert called["type"] == "daily"
    assert flags.updated


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
            jobs.append((func, trigger, kw))

        def start(self):
            self.running = True

    fake = FakeScheduler()
    monkeypatch.setattr(mod, "scheduler", fake)

    mod.schedule_dm_tasks("bot")

    assert fake.running
    assert len(jobs) == 2
    cron_job = jobs[0]
    assert cron_job[1] == "cron"
    assert cron_job[2]["hour"] == 0
    assert cron_job[2]["minute"] == 0
    assert cron_job[2]["timezone"] == "UTC"


@pytest.mark.asyncio
async def test_send_embed_dm(monkeypatch):
    from bot import dm_scheduler as mod

    monkeypatch.setattr(mod, "get_dm_image", lambda t: "http://img.png")

    class FakeUser:
        def __init__(self):
            self.embed = None

        async def send(self, *, embed: discord.Embed):
            self.embed = embed

    user = FakeUser()
    await mod.send_embed_dm(user, "hi", "daily")

    assert isinstance(user.embed, discord.Embed)
    assert user.embed.image.url == "http://img.png"


@pytest.mark.asyncio
async def test_send_embed_dm_fallback(monkeypatch):
    from bot import dm_scheduler as mod

    monkeypatch.setattr(mod, "get_dm_image", lambda t: "")

    class FakeUser:
        def __init__(self):
            self.embed = None

        async def send(self, *, embed: discord.Embed):
            self.embed = embed

    user = FakeUser()
    await mod.send_embed_dm(user, "hi", "daily")

    assert user.embed.image.url == Config.DEFAULT_DM_IMAGE_URL
