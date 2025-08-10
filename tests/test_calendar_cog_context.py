import importlib
import pathlib
import sys
import types

import pytest
from flask import Flask, has_app_context

services_pkg = types.ModuleType("services")
services_pkg.__path__ = [str(pathlib.Path(__file__).resolve().parents[1] / "services")]
sys.modules["services"] = services_pkg

main_app_pkg = types.ModuleType("main_app")
main_app_pkg.app = Flask("test")
sys.modules["main_app"] = main_app_pkg

calendar_cog = importlib.import_module("bot.cogs.calendar_cog")


@pytest.mark.asyncio
async def test_calendar_cog_initializes_without_service(monkeypatch):
    monkeypatch.setattr(calendar_cog.tasks.Loop, "start", lambda self: None)
    cog = calendar_cog.CalendarCog(types.SimpleNamespace())
    assert cog.service is None


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


@pytest.mark.asyncio
async def test_sync_loop_builds_service_with_app_context(monkeypatch):
    monkeypatch.setattr(calendar_cog.tasks.Loop, "start", lambda self: None)

    called: dict[str, bool] = {}

    class DummyService:
        def __init__(self, *_, **__):
            self.service = None

        def _build_service(self) -> None:
            called["build"] = has_app_context()
            self.service = object()

        async def sync(self) -> None:
            called["sync"] = True

    monkeypatch.setattr(calendar_cog, "CalendarService", DummyService)

    async def ready():
        return None

    bot = types.SimpleNamespace(wait_until_ready=ready)
    cog = calendar_cog.CalendarCog(bot)

    await cog.sync_loop()

    assert called.get("build") is True
    assert called.get("sync")
