import types
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import discord
import pytest
import logging

from bot.cogs.calendar_cog import CalendarCog, should_send_daily, should_send_weekly


class DummyUser:
    def __init__(self) -> None:
        self.id = 1
        self.embed: discord.Embed | None = None

    async def send(self, *, embed: discord.Embed) -> None:
        self.embed = embed


@pytest.mark.asyncio
async def test_send_events_dm_builds_embed():
    cog = CalendarCog.__new__(CalendarCog)
    cog._get_user_timezone = lambda uid: ZoneInfo("UTC")
    user = DummyUser()
    events = [{"title": "Ping", "event_time": datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)}]
    await CalendarCog._send_events_dm(cog, user, events, "Title")
    assert isinstance(user.embed, discord.Embed)
    assert user.embed.fields[0].name == "Ping"


def test_should_send_daily_weekly():
    morning = datetime(2025, 1, 1, 8, 0, tzinfo=timezone.utc)
    assert should_send_daily(morning)
    assert not should_send_daily(morning - timedelta(hours=1))

    sunday = datetime(2025, 1, 5, 12, 0, tzinfo=timezone.utc)
    assert should_send_weekly(sunday)
    assert not should_send_weekly(sunday + timedelta(days=1))


@pytest.mark.asyncio
async def test_send_events_dm_converts_timezone():
    cog = CalendarCog.__new__(CalendarCog)
    cog._get_user_timezone = lambda uid: ZoneInfo("Asia/Tokyo")
    user = DummyUser()
    events = [{"title": "Ping", "event_time": datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)}]
    await CalendarCog._send_events_dm(cog, user, events, "Title")
    assert "21:00" in user.embed.fields[0].value


class DummyInteraction:
    def __init__(self) -> None:
        self.user = DummyUser()
        self.response = types.SimpleNamespace()

        async def send_message(message, *, ephemeral=False, view=None):
            self.message = message
            self.ephemeral = ephemeral

        self.response.send_message = send_message


@pytest.mark.asyncio
async def test_cmd_today_sends_embed(monkeypatch):
    cog = CalendarCog.__new__(CalendarCog)
    cog._get_user_timezone = lambda uid: ZoneInfo("UTC")

    async def fake_events():
        return [{"title": "Ping", "event_time": datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)}]

    cog.service = types.SimpleNamespace(get_events_today=fake_events)

    async def fake_send_dm(self, user, events, title):
        user.embed = discord.Embed(title=title)

    monkeypatch.setattr(CalendarCog, "_send_events_dm", fake_send_dm)
    monkeypatch.setattr("bot.cogs.calendar_cog.t", lambda key, **k: key)

    interaction = DummyInteraction()
    await CalendarCog.cmd_today.callback(cog, interaction)

    assert interaction.ephemeral
    assert isinstance(interaction.user.embed, discord.Embed)


@pytest.mark.asyncio
async def test_setup_skips_duplicate_registration(monkeypatch):
    from discord.ext import commands

    from bot.cogs import calendar_cog as mod

    bot = commands.Bot(command_prefix="!", intents=discord.Intents.none())

    await mod.setup(bot)
    await mod.setup(bot)  # second call should not register again

    cmds = [c for c in bot.tree.get_commands() if c.name == "calendar"]
    assert len(cmds) == 1


@pytest.mark.asyncio
async def test_sync_loop_builds_and_syncs(monkeypatch):
    cog = CalendarCog.__new__(CalendarCog)

    async def ready():
        return None

    cog.bot = types.SimpleNamespace(wait_until_ready=ready)

    called: dict[str, bool] = {}

    class DummyService:
        def __init__(self) -> None:
            self.service = None

        def _build_service(self) -> None:
            called["build"] = True
            self.service = object()

        async def sync(self) -> None:
            called["sync"] = True

    cog.service = DummyService()

    await cog.sync_loop()

    assert called.get("build")
    assert called.get("sync")


@pytest.mark.asyncio
async def test_sync_loop_skips_when_unconfigured(monkeypatch, caplog):
    cog = CalendarCog.__new__(CalendarCog)

    async def ready():
        return None

    cog.bot = types.SimpleNamespace(wait_until_ready=ready)

    called: dict[str, bool] = {}

    class DummyService:
        def __init__(self) -> None:
            self.service = None

        def _build_service(self) -> None:
            called["build"] = True

        async def sync(self) -> None:  # pragma: no cover - should not run
            called["sync"] = True

    cog.service = DummyService()

    with caplog.at_level(logging.WARNING):
        await cog.sync_loop()

    assert called.get("build")
    assert "Calendar service not configured" in caplog.text
    assert "sync" not in called
