from config import Config
from modules import champion as champion_mod


class FakeWebhook:
    def __init__(self, url):
        self.url = url
        self.called = False
        self.kwargs = {}

    def send(
        self,
        content: str,
        webhook_url=None,
        image_url=None,
        *,
        event_channel=False,
    ):
        self.called = True
        self.kwargs = {
            "content": content,
            "image_url": image_url,
            "event_channel": event_channel,
        }
        # ensure file exists
        assert image_url
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


def test_run_champion_autopilot(monkeypatch, tmp_path):
    from champion import autopilot as autopilot_mod

    def fake_generate(username="Champion"):
        path = tmp_path / f"{username}.png"
        path.write_bytes(b"img")
        return str(path)

    def fake_send(content: str, image_url: str):
        fake_send.called = True
        fake_send.kwargs = {"content": content, "image_url": image_url}
        return 204

    monkeypatch.setattr(autopilot_mod, "generate_champion_poster", fake_generate)
    monkeypatch.setattr(autopilot_mod, "send_discord_webhook", fake_send)

    assert autopilot_mod.run_champion_autopilot(month="June", username="Tester")
    assert fake_send.called
    assert "June" in fake_send.kwargs["content"]
    assert fake_send.kwargs["image_url"].startswith("http")


def test_run_champion_autopilot_error(monkeypatch, tmp_path):
    from champion import autopilot as autopilot_mod

    def fake_generate(username="Champion"):
        path = tmp_path / f"{username}.png"
        path.write_bytes(b"img")
        return str(path)

    def fake_send(*args, **kwargs):
        raise RuntimeError("fail")

    monkeypatch.setattr(autopilot_mod, "generate_champion_poster", fake_generate)
    monkeypatch.setattr(autopilot_mod, "send_discord_webhook", fake_send)

    assert autopilot_mod.run_champion_autopilot() is False


def test_run_champion_autopilot_bad_status(monkeypatch, tmp_path):
    from champion import autopilot as autopilot_mod

    def fake_generate(username="Champion"):
        path = tmp_path / f"{username}.png"
        path.write_bytes(b"img")
        return str(path)

    def fake_send(*args, **kwargs):
        return 500

    monkeypatch.setattr(autopilot_mod, "generate_champion_poster", fake_generate)
    monkeypatch.setattr(autopilot_mod, "send_discord_webhook", fake_send)

    assert autopilot_mod.run_champion_autopilot() is False
