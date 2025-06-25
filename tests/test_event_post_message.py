import importlib
from pathlib import Path

import mongo_service
from tests.test_admin_auth import login_with_role


class FakeWebhook:
    def __init__(self, url):
        self.url = url
        self.calls = 0

    def send(self, content: str, webhook_url=None, file_path=None, *, event_channel=False):
        self.calls += 1
        assert Path(file_path).is_file()
        return True


def test_post_event_single_message(client, monkeypatch, tmp_path):
    admin_mod = importlib.import_module("blueprints.admin")
    admin_mod.db = mongo_service.db

    poster = tmp_path / "poster.png"
    poster.write_text("img")

    event_id = (
        admin_mod.db["events"]
        .insert_one({"title": "T", "description": "d", "event_time": "soon"})
        .inserted_id
    )

    fake = FakeWebhook("http://example.com")
    monkeypatch.setattr(admin_mod, "WebhookAgent", lambda url: fake)
    monkeypatch.setattr(admin_mod, "generate_event_poster", lambda event: str(poster))

    login_with_role(client, "R4")
    resp = client.post(f"/admin/events/post/{event_id}")
    assert resp.status_code == 302
    assert fake.calls == 1

    admin_mod.db["events"].delete_one({"_id": event_id})
