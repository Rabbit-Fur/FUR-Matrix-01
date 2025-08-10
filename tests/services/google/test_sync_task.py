from flask import Flask


def test_start_google_sync_runs_job_with_app_context(monkeypatch):
    import services.google.sync_task as task_mod

    task_mod._scheduler = None
    app = Flask("test_app")
    mongo_db = object()
    called = {}

    def fake_sync_to_mongodb(*, mongo_db: object, **kwargs):
        from flask import current_app

        called["app"] = current_app.name
        called["db"] = mongo_db
        return 1

    monkeypatch.setattr(task_mod, "sync_to_mongodb", fake_sync_to_mongodb)

    class DummyScheduler:
        def __init__(self):
            self.jobs = []
            self.running = False

        def add_job(self, func, trigger, minutes, id, replace_existing):
            self.jobs.append(func)

        def start(self):
            self.running = True

    scheduler = DummyScheduler()
    monkeypatch.setattr(task_mod, "BackgroundScheduler", lambda: scheduler)

    task_mod.start_google_sync(app, mongo_db)

    assert scheduler.running
    assert len(scheduler.jobs) == 1

    scheduler.jobs[0]()
    assert called["app"] == app.name
    assert called["db"] is mongo_db
