from datetime import datetime, timezone

import discord
from config import Config
import pytest


@pytest.mark.asyncio
async def test_send_embed_dm(monkeypatch):
    from bot import dm_utils as mod

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
    from bot import dm_utils as mod

    monkeypatch.setattr(mod, "get_dm_image", lambda t: "")

    class FakeUser:
        def __init__(self):
            self.embed = None

        async def send(self, *, embed: discord.Embed):
            self.embed = embed

    user = FakeUser()
    await mod.send_embed_dm(user, "hi", "daily")

    assert user.embed.image.url == Config.DEFAULT_DM_IMAGE_URL


@pytest.mark.asyncio
async def test_tick_sends_reminders():
    from bot.dm_scheduler import DMReminderScheduler

    sent: list[tuple[int, str]] = []

    async def send_dm(uid: int, msg: str) -> None:
        sent.append((uid, msg))

    class FakeParticipants:
        def find(self, query):
            return self

        async def to_list(self, length=None):
            return [{"user_id": "1"}]

    class FakeEventsCollection:
        def __init__(self):
            self.database = {"event_participants": FakeParticipants()}

    class FakeService:
        def __init__(self):
            self.events = FakeEventsCollection()

        async def list_upcoming_events(self):
            return [
                {
                    "_id": 1,
                    "title": "Ping",
                    "event_time": datetime.utcnow().replace(tzinfo=timezone.utc),
                }
            ]

    scheduler = DMReminderScheduler(FakeService(), send_dm)
    await scheduler.tick()

    assert sent and sent[0][0] == 1 and "Ping" in sent[0][1]


@pytest.mark.asyncio
async def test_tick_avoids_duplicate_dms():
    from bot.dm_scheduler import DMReminderScheduler

    sent: list[tuple[int, str]] = []

    async def send_dm(uid: int, msg: str) -> None:
        sent.append((uid, msg))

    class FakeParticipants:
        def find(self, query):
            return self

        async def to_list(self, length=None):
            return [{"user_id": "1"}]

    class FakeEventsCollection:
        def __init__(self):
            self.database = {"event_participants": FakeParticipants()}

    class FakeService:
        def __init__(self):
            self.events = FakeEventsCollection()

        async def list_upcoming_events(self):
            return [
                {
                    "_id": 99,
                    "title": "Test Event",
                    "event_time": datetime.utcnow().replace(tzinfo=timezone.utc),
                }
            ]

    scheduler = DMReminderScheduler(FakeService(), send_dm)

    await scheduler.tick()
    await scheduler.tick()

    assert len(sent) == 1
