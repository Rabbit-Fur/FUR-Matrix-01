from datetime import datetime
from pathlib import Path

from config import Config
from modules import weekly_report as report_mod


class FakeParticipants:
    def aggregate(self, pipeline):
        return [{"_id": "user", "count": 1}]


class FakeEvents:
    def find(self, query, fields):
        return self

    def sort(self, *args):
        return [{"title": "Event", "event_time": datetime.utcnow()}]


def fake_get_collection(name):
    if name == "participants":
        return FakeParticipants()
    return FakeEvents()


class FakeWebhook:
    def __init__(self, url):
        self.url = url
        self.sent = False

    def send(self, content: str, webhook_url=None, file_path=None):
        self.sent = True
        assert content.startswith("```")
        return True


def fake_generate(part, upcoming, filename):
    path = Path(filename)
    path.write_text("report")
    return str(path)


def test_post_report(monkeypatch):
    monkeypatch.setattr(Config, "DISCORD_WEBHOOK_URL", "http://example.com")
    monkeypatch.setattr(report_mod, "generate_markdown_report", fake_generate)
    monkeypatch.setattr(report_mod, "get_collection", fake_get_collection)
    monkeypatch.setattr(report_mod, "WebhookAgent", FakeWebhook)

    assert report_mod.post_report() is True
