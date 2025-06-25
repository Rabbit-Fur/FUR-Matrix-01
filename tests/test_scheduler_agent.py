import sys
import types


def test_scheduler_jobs(monkeypatch):
    schedule_mod = types.ModuleType("schedule")
    jobs = []

    class FakeEvery:
        def __init__(self, interval):
            self.interval = interval

        @property
        def minutes(self):
            return self

        @property
        def hours(self):
            return self

        @property
        def seconds(self):
            return self

        def do(self, func, *args, **kwargs):
            jobs.append((self.interval, func))
            return object()

    schedule_mod.every = lambda interval: FakeEvery(interval)
    sys.modules["schedule"] = schedule_mod

    import importlib

    agent_mod = importlib.reload(__import__("agents.scheduler_agent", fromlist=["SchedulerAgent"]))

    monkeypatch.setattr(agent_mod, "start_google_sync", lambda *a, **k: None)
    monkeypatch.setattr(agent_mod, "sync_google_calendar", lambda: None)
    monkeypatch.setattr(agent_mod, "run_champion_autopilot", lambda **k: None)

    agent = agent_mod.SchedulerAgent()
    agent.schedule_google_sync(interval_minutes=5)
    agent.schedule_champion_autopilot(interval_hours=1)

    assert len(agent.jobs) == 2
    assert jobs[0][0] == 5
    assert jobs[1][0] == 1
