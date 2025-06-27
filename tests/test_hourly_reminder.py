import asyncio
import types
from datetime import datetime

import pytest

from bot.cogs import hourly_reminder_cog as rem_mod


def fake_t(key, *, lang="en", **kwargs):
    if key == "reminder_hourly":
        return f"Reminder: {kwargs.get('time')} UTC"
    return key


class DummyChannel:
    def __init__(self, cid=1):
        self.id = cid
        self.message = None

    async def send(self, msg):
        self.message = msg


class DummyCollection:
    def __init__(self, count=0):
        self.count = count

    def count_documents(self, _filter):
        return self.count


@pytest.mark.asyncio
async def test_sends_if_open_tasks(monkeypatch):
    channel = DummyChannel()

    async def ready():
        return None

    bot = types.SimpleNamespace(wait_until_ready=ready, get_channel=lambda cid: channel)

    monkeypatch.setattr(rem_mod.tasks.Loop, "start", lambda self, *a, **k: None)
    monkeypatch.setattr(rem_mod, "t", fake_t)
    monkeypatch.setattr(rem_mod, "get_collection", lambda name: DummyCollection(count=1))
    now = datetime.utcnow()
    monkeypatch.setattr(rem_mod, "datetime", types.SimpleNamespace(utcnow=lambda: now))

    cog = rem_mod.HourlyReminderCog(bot)
    await cog.reminder_loop()

    assert channel.message and "UTC" in channel.message


@pytest.mark.asyncio
async def test_no_send_if_recent(monkeypatch):
    channel = DummyChannel()

    async def ready():
        return None

    bot = types.SimpleNamespace(wait_until_ready=ready, get_channel=lambda cid: channel)

    monkeypatch.setattr(rem_mod.tasks.Loop, "start", lambda self, *a, **k: None)
    monkeypatch.setattr(rem_mod, "t", fake_t)
    monkeypatch.setattr(rem_mod, "get_collection", lambda name: DummyCollection(count=1))
    now = datetime.utcnow()
    monkeypatch.setattr(rem_mod, "datetime", types.SimpleNamespace(utcnow=lambda: now))

    cog = rem_mod.HourlyReminderCog(bot)
    cog._last_sent[channel.id] = now
    await cog.reminder_loop()

    assert channel.message is None
