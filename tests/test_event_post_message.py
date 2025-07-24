import importlib

import mongo_service
from tests.test_admin_auth import login_with_role


class FakeWebhook:
    def __init__(self, url):
        self.url = url
        self.calls = 0

    def send(self, content: str, webhook_url=None, image_url=None, *, event_channel=False):
        self.calls += 1
        assert image_url.startswith("http")
        return True


def test_post_event_single_message(client, monkeypatch, tmp_path):
    admin_mod = importlib.import_module("blueprints.admin")

    poster = tmp_path / "poster.png"
    poster.write_text("img")

    event_id = (
        mongo_service.get_collection("events")
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

    mongo_service.get_collection("events").delete_one({"_id": event_id})
