import asyncio
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import discord
import pytest

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
