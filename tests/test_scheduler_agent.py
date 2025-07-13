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

    called = {}

    def fake_start_google_sync(interval_minutes=None, *a, **k):
        called["minutes"] = interval_minutes

    monkeypatch.setattr(agent_mod, "start_google_sync", fake_start_google_sync)
    monkeypatch.setattr(agent_mod, "run_champion_autopilot", lambda **k: None)

    agent = agent_mod.SchedulerAgent()
    agent.schedule_google_sync(interval_minutes=5)
    agent.schedule_champion_autopilot(interval_hours=1)

    assert called["minutes"] == 5
    assert len(agent.jobs) == 1
    assert jobs[0][0] == 1


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
    called = {}

    import importlib

    agent_mod = importlib.reload(__import__("agents.scheduler_agent", fromlist=["SchedulerAgent"]))

    def fake_start(interval_minutes=None, *a, **k):
        called["minutes"] = interval_minutes

    monkeypatch.setattr(agent_mod, "start_google_sync", fake_start)

    agent = agent_mod.SchedulerAgent()
    agent.schedule_google_sync(interval_minutes=1)

    assert called.get("minutes") == 1
    assert agent.jobs == []
