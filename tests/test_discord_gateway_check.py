import asyncio
import logging
import sys
import types

import pytest


@pytest.mark.asyncio
async def test_analyze_warns_on_time_sleep(monkeypatch, caplog):
    from codex.diagnostics import discord_gateway_check as mod

    class FakeScheduler:
        async def tick(self):
            import time

            time.sleep(1)

    fake_mod = types.SimpleNamespace(DMReminderScheduler=FakeScheduler)
    monkeypatch.setitem(sys.modules, "bot.dm_scheduler", fake_mod)

    with caplog.at_level(logging.WARNING):
        await mod.analyze_scheduler_tick()
    assert "time.sleep()" in caplog.text


@pytest.mark.asyncio
async def test_analyze_handles_async_function(monkeypatch, caplog):
    from codex.diagnostics import discord_gateway_check as mod

    class FakeScheduler:
        async def tick(self):
            await asyncio.sleep(0)

    fake_mod = types.SimpleNamespace(DMReminderScheduler=FakeScheduler)
    monkeypatch.setitem(sys.modules, "bot.dm_scheduler", fake_mod)

    with caplog.at_level(logging.INFO):
        await mod.analyze_scheduler_tick()
    assert "Kein blockierender sleep" in caplog.text
