import os
from pathlib import Path

from config import Config
from modules import champion as champion_mod


class FakeWebhook:
    def __init__(self, url):
        self.url = url
        self.called = False
        self.kwargs = {}

    def send(self, content: str, webhook_url=None, file_path=None):
        self.called = True
        self.kwargs = {"content": content, "file_path": file_path}
        # ensure file exists
        assert file_path and Path(file_path).is_file()
        return True


def test_post_champion_poster(monkeypatch, tmp_path):
    monkeypatch.setattr(Config, "DISCORD_WEBHOOK_URL", "http://example.com")

    def fake_generate(username="Champion"):
        path = tmp_path / f"{username}.png"
        path.write_bytes(b"img")
        return str(path)

    monkeypatch.setattr(champion_mod, "generate_champion_poster", fake_generate)
    monkeypatch.setattr(champion_mod, "WebhookAgent", FakeWebhook)

    success = champion_mod.post_champion_poster("Tester")
    assert success
