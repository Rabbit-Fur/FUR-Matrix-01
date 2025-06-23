from datetime import datetime
from types import SimpleNamespace

import pytest

import bot.cogs.newsletter_autopilot as mod


def test_should_send_newsletter_true():
    sunday_noon = datetime(2024, 8, 18, 12, 0)
    assert mod.should_send_newsletter(sunday_noon)


def test_should_send_newsletter_false():
    sunday_late = datetime(2024, 8, 18, 13, 0)
    monday_noon = datetime(2024, 8, 19, 12, 0)
    assert not mod.should_send_newsletter(sunday_late)
    assert not mod.should_send_newsletter(monday_noon)


class FakeCollection:
    def __init__(self, should_block=False):
        self.should_block = should_block

    def find(self, *a, **kw):
        return self

    def sort(self, *a, **kw):
        return [{"title": "Event", "event_time": datetime.utcnow()}]

    def find_one(self, query):
        if self.should_block:
            return {"discord_id": query["discord_id"]}
        return None


class FakeMember(SimpleNamespace):
    bot = False

    async def send(self, *_):
        self.sent = True


class FakeGuild(SimpleNamespace):
    pass


class FakeBot(SimpleNamespace):
    def get_guild(self, gid):
        return self.guild

    async def wait_until_ready(self):
        return


@pytest.mark.asyncio
async def test_opt_out(monkeypatch):
    guild = FakeGuild(members=[FakeMember(id=1), FakeMember(id=2)])
    bot = FakeBot(guild=guild)

    def fake_get_collection(name):
        if name == "newsletter_optout":
            return FakeCollection(should_block=True)
        return FakeCollection()

    monkeypatch.setattr(mod.tasks.Loop, "start", lambda self: None)
    monkeypatch.setattr(mod, "get_collection", fake_get_collection)
    monkeypatch.setattr(mod.Config, "DISCORD_GUILD_ID", 1)

    cog = mod.NewsletterAutopilot(bot)
    await cog.send_newsletters()

    # first member blocked, second blocked too because collection returns block
    assert cog.blocked == 2
    assert cog.sent == 0


def test_should_send_daily_overview():
    morning = datetime(2024, 8, 19, 8, 0)
    assert mod.should_send_daily_overview(morning)
    later = datetime(2024, 8, 19, 9, 0)
    assert not mod.should_send_daily_overview(later)


@pytest.mark.asyncio
async def test_daily_opt_out(monkeypatch):
    guild = FakeGuild(members=[FakeMember(id=1), FakeMember(id=2)])
    bot = FakeBot(guild=guild)

    def fake_get_collection(name):
        if name == "newsletter_optout":
            return FakeCollection(should_block=True)
        return FakeCollection()

    monkeypatch.setattr(mod.tasks.Loop, "start", lambda self: None)
    monkeypatch.setattr(mod, "get_collection", fake_get_collection)
    monkeypatch.setattr(mod.Config, "DISCORD_GUILD_ID", 1)

    cog = mod.NewsletterAutopilot(bot)
    await cog.send_daily_overview()

    assert cog.blocked == 2
    assert cog.sent == 0
