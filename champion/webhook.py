"""Simple helper to send champion posters via Discord webhook."""

import logging

import requests

from config import Config


def send_discord_webhook(content: str, image_url: str) -> int | None:
    """Send a Discord webhook with an embed image."""

    webhook_url = Config.DISCORD_WEBHOOK_URL
    try:
        data = {"content": content, "embeds": [{"image": {"url": image_url}}]}
        response = requests.post(webhook_url, json=data)
        return response.status_code
    except Exception as exc:  # noqa: BLE001
        logging.error("Failed to send Discord webhook: %s", exc)
        return None
