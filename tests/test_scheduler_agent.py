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


def test_monthly_champion_job(monkeypatch):
    schedule_mod = types.ModuleType("schedule")
    jobs = []

    class FakeEvery:
        def __init__(self, interval):
            self.interval = interval

        @property
        def days(self):
            return self

        def do(self, func, *args, **kwargs):
            jobs.append((self.interval, func))
            return object()

    schedule_mod.every = lambda interval: FakeEvery(interval)
    sys.modules["schedule"] = schedule_mod

    import importlib

    agent_mod = importlib.reload(__import__("agents.scheduler_agent", fromlist=["SchedulerAgent"]))

    fake_coll = types.SimpleNamespace()
    fake_coll.find = lambda: fake_coll
    fake_coll.sort = lambda *a, **kw: fake_coll
    fake_coll.limit = lambda n: [{"username": "Top", "score": 10}]
    monkeypatch.setattr(agent_mod, "get_collection", lambda name: fake_coll)

    added = {}

    def fake_add(username, honor_title, month, poster_url):
        added["user"] = username
        added["poster"] = poster_url

    monkeypatch.setattr(agent_mod.champion_data, "add_champion", fake_add)
    monkeypatch.setattr(agent_mod.champion_data, "generate_champion_poster", lambda u: "img.png")
    called = {}
    monkeypatch.setattr(
        agent_mod, "run_champion_autopilot", lambda **k: called.setdefault("ok", True)
    )

    agent = agent_mod.SchedulerAgent()
    agent.schedule_monthly_champion_job()

    assert len(agent.jobs) == 1
    assert jobs[0][0] == 30

    jobs[0][1]()
    assert added["user"] == "Top"
    assert called.get("ok")


def test_google_sync_job_uses_app_context(monkeypatch):
    schedule_mod = types.ModuleType("schedule")
    called = {}

    class FakeEvery:
        def __init__(self, interval):
            self.interval = interval

        @property
        def minutes(self):
            return self

        def do(self, func, *args, **kwargs):
            func()
            return object()

    schedule_mod.every = lambda interval: FakeEvery(interval)
    sys.modules["schedule"] = schedule_mod

    import importlib

    agent_mod = importlib.reload(__import__("agents.scheduler_agent", fromlist=["SchedulerAgent"]))

    monkeypatch.setattr(agent_mod, "start_google_sync", lambda *a, **k: None)

    def fake_get_app():
        from web import create_app

        return create_app()

    monkeypatch.setattr(agent_mod, "_get_app", fake_get_app)

    def fake_sync():
        from flask import current_app

        called["app"] = current_app.name

    monkeypatch.setattr(agent_mod, "sync_google_calendar", fake_sync)

    agent = agent_mod.SchedulerAgent()
    agent.schedule_google_sync(interval_minutes=1)

    assert called.get("app") == "web"
