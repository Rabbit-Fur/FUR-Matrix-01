from flask import Flask


def test_schedule_google_sync_injects_dependencies(monkeypatch):
    from agents import scheduler_agent as agent_mod

    app = Flask(__name__)
    db = object()
    called = {}

    def fake_start_google_sync(app_arg, mongo_db_arg):
        called["app"] = app_arg
        called["db"] = mongo_db_arg

    monkeypatch.setattr(agent_mod, "start_google_sync", fake_start_google_sync)

    agent = agent_mod.SchedulerAgent(app, db)
    agent.schedule_google_sync()

    assert called["app"] is app
    assert called["db"] is db
