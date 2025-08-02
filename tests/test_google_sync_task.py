import asyncio
import sys
import types


def test_google_sync_task_runs(monkeypatch):
    sys.modules.setdefault("schedule", types.ModuleType("schedule"))

    import src.agents.scheduler_agent as agent_mod
    import utils.google_sync_task as task_mod

    called = {"count": 0}

    def fake_sync():
        called["count"] += 1

    monkeypatch.setattr(task_mod, "sync_to_mongodb", fake_sync)

    def fake_start():
        asyncio.run(task_mod.google_sync_loop.coro())

    monkeypatch.setattr(task_mod.google_sync_loop, "start", fake_start)

    agent = agent_mod.SchedulerAgent()
    agent.schedule_google_sync(interval_minutes=1)

    assert called["count"] == 1


def test_start_google_sync_pushes_app_context(monkeypatch):
    sys.modules.setdefault("schedule", types.ModuleType("schedule"))

    import utils.google_sync_task as task_mod

    called = {}

    def fake_sync():
        from flask import current_app

        called["app"] = current_app.name

    monkeypatch.setattr(task_mod, "sync_to_mongodb", fake_sync)

    def fake_start():
        asyncio.run(task_mod.google_sync_loop.coro())

    monkeypatch.setattr(task_mod.google_sync_loop, "start", fake_start)

    task_mod.start_google_sync(interval_minutes=1)

    assert called.get("app")
