import importlib
import logging

import pytest


@pytest.fixture
def reload_discord_util(monkeypatch):
    """Reload ``utils.discord_util`` with fallback mode enabled."""

    def _reload(webhook_url: str | None = None):
        monkeypatch.setenv("ENABLE_DISCORD_BOT", "false")
        if webhook_url is None:
            monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)
        else:
            monkeypatch.setenv("DISCORD_WEBHOOK_URL", webhook_url)

        import utils.discord_util as discord_util

        return importlib.reload(discord_util)

    return _reload


def test_send_discord_message_skips_without_webhook(monkeypatch, caplog, reload_discord_util):
    mod = reload_discord_util(webhook_url=None)

    def _unexpected_post(*args, **kwargs):  # pragma: no cover - defensive
        raise AssertionError("requests.post should not be called when webhook URL is missing")

    monkeypatch.setattr(mod.requests, "post", _unexpected_post)

    with caplog.at_level(logging.WARNING):
        result = mod.send_discord_message(123, "Hallo Welt")

    assert result is False
    assert any(
        "DISCORD_WEBHOOK_URL fehlt" in message for message in caplog.messages
    ), "Expected warning about missing webhook URL"


def test_send_discord_message_posts_with_webhook(monkeypatch, caplog, reload_discord_util):
    mod = reload_discord_util(webhook_url="https://example.com/webhook")

    class _DummyResponse:
        status_code = 204
        text = "ok"

    captured = {}

    def _fake_post(url, json=None, **_kwargs):
        captured["url"] = url
        captured["json"] = json
        return _DummyResponse()

    monkeypatch.setattr(mod.requests, "post", _fake_post)

    with caplog.at_level(logging.INFO):
        result = mod.send_discord_message(123, "Hallo Welt", image_url=None)

    assert result is True
    assert captured["url"] == "https://example.com/webhook"
    assert captured["json"] == {"content": "Hallo Welt"}
    assert any("Webhook erfolgreich" in message for message in caplog.messages)
