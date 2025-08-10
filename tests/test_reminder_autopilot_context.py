import importlib
import pathlib
import sys
import types

import pytest

services_pkg = types.ModuleType("services")
services_pkg.__path__ = [str(pathlib.Path(__file__).resolve().parents[1] / "services")]
sys.modules["services"] = services_pkg

autopilot_mod = importlib.import_module("bot.cogs.reminder_autopilot")


@pytest.mark.asyncio
async def test_reminder_autopilot_runs_without_app_context(monkeypatch):
    monkeypatch.setattr(autopilot_mod.tasks.Loop, "start", lambda self: None)
    bot = types.SimpleNamespace()
    cog = autopilot_mod.ReminderAutopilot(bot)

    monkeypatch.setattr(autopilot_mod, "get_service", lambda settings: object())
    monkeypatch.setattr(autopilot_mod, "list_upcoming_events", lambda *a, **k: [])
    monkeypatch.setattr(autopilot_mod, "is_production", lambda: True)

    await cog.run_reminder_check()
