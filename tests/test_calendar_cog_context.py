import importlib
import pathlib
import sys
import types

import pytest

services_pkg = types.ModuleType("services")
services_pkg.__path__ = [str(pathlib.Path(__file__).resolve().parents[1] / "services")]
sys.modules["services"] = services_pkg

calendar_cog = importlib.import_module("bot.cogs.calendar_cog")


@pytest.mark.asyncio
async def test_calendar_cog_loops_without_app_context(monkeypatch):
    monkeypatch.setattr(calendar_cog.tasks.Loop, "start", lambda self: None)

    async def ready():
        return None

    bot = types.SimpleNamespace(
        wait_until_ready=ready, get_guild=lambda gid: types.SimpleNamespace(members=[])
    )
    cog = calendar_cog.CalendarCog(bot)

    class DummyService:
        def __init__(self) -> None:
            self.service = object()

        def _build_service(self) -> None:
            pass

        async def sync(self) -> None:
            return None

        async def get_events_today(self):
            return []

        async def get_events_week(self):
            return []

    cog.service = DummyService()

    monkeypatch.setattr(calendar_cog, "should_send_daily", lambda dt: False)
    monkeypatch.setattr(calendar_cog, "should_send_weekly", lambda dt: False)

    await cog.sync_loop()
    await cog.daily_loop()
    await cog.weekly_loop()
