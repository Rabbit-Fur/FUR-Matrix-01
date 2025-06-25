import asyncio
import sys
import types


def test_google_sync_task_runs(monkeypatch):
    sys.modules.setdefault("schedule", types.ModuleType("schedule"))

    import agents.scheduler_agent as agent_mod
    import utils.google_sync_task as task_mod

    called = {"count": 0}

    def fake_sync():
        called["count"] += 1

    monkeypatch.setattr(task_mod, "sync_google_calendar", fake_sync)

    def fake_start():
        asyncio.run(task_mod.google_sync_loop.coro())

    monkeypatch.setattr(task_mod.google_sync_loop, "start", fake_start)

    agent = agent_mod.SchedulerAgent()
    agent.schedule_google_sync(interval_minutes=1)

    assert called["count"] == 1
