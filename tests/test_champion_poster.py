import os

from champion import webhook
from config import Config
from utils import champion_data


class DummyResponse:
    def __init__(self, status_code=204):
        self.status_code = status_code


def test_generate_poster_and_webhook(monkeypatch, tmp_path):
    # redirect output to temp folder
    monkeypatch.setattr(Config, "STATIC_FOLDER", str(tmp_path))
    monkeypatch.setattr(Config, "POSTER_OUTPUT_PATH", str(tmp_path))

    # dummy request.post
    def fake_post(url, json=None, **_):
        fake_post.called_url = url
        assert json and "embeds" in json
        return DummyResponse()

    monkeypatch.setattr(webhook.requests, "post", fake_post)
    monkeypatch.setattr(Config, "DISCORD_WEBHOOK_URL", "http://example.com")

    path = champion_data.generate_champion_poster("Tester")
    assert os.path.isfile(path)

    status = webhook.send_discord_webhook("hello", "http://img")
    assert status == 204
    assert fake_post.called_url == "http://example.com"
