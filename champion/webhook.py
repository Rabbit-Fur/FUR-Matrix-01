"""Simple helper to send champion posters via Discord webhook."""

import requests

from config import Config


def send_discord_webhook(content: str, file_path: str) -> int:
    """Upload a file to the configured Discord webhook."""

    webhook_url = Config.DISCORD_WEBHOOK_URL
    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {"content": content}
        response = requests.post(webhook_url, data=data, files=files)
    return response.status_code
