"""Simple helper to send champion posters via Discord webhook."""

import logging

import requests

from config import Config


def send_discord_webhook(content: str, file_path: str) -> int | None:
    """Upload a file to the configured Discord webhook."""

    webhook_url = Config.DISCORD_WEBHOOK_URL
    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"content": content}
            response = requests.post(webhook_url, data=data, files=files)
        return response.status_code
    except Exception as exc:  # noqa: BLE001
        logging.error("Failed to send Discord webhook: %s", exc)
        return None
