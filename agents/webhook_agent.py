"""Central handler for outgoing webhook messages (Discord, CI, events)."""

import logging
from typing import Optional

import requests


class WebhookAgent:
    def __init__(self, default_url: Optional[str] = None):
        self.default_url = default_url

    def send(
        self,
        content: str,
        webhook_url: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> bool:
        url = webhook_url or self.default_url
        if not url:
            logging.error("❌ Kein Webhook-URL angegeben")
            return False

        data = {"content": content}
        files = {"file": open(file_path, "rb")} if file_path else None

        try:
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()
            logging.info(f"📤 Webhook erfolgreich gesendet ({response.status_code})")
            return True
        except Exception as e:
            logging.error(f"❌ Fehler beim Webhook-Senden: {e}")
            return False

    def send_log_notification(self, log_content: str) -> bool:
        return self.send(content=f"📘 Neue Log-Datei:\n```{log_content[:1800]}```")

    def send_champion_announcement(
        self, username: str, title: str, month: str, file_path: str
    ) -> bool:
        message = f"🏆 **{title}**\n{username} wurde Champion im Monat {month}!"
        return self.send(content=message, file_path=file_path)

    def send_error(self, context: str, error: Exception) -> bool:
        return self.send(content=f"❌ Fehler in `{context}`:\n```{str(error)}```")
