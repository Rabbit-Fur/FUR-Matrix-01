"""Central handler for outgoing webhook messages (Discord, CI, events)."""

import logging
from typing import Optional

import requests

from config import Config
from utils.discord_util import send_discord_message


class WebhookAgent:
    def __init__(self, default_url: Optional[str] = None):
        self.default_url = default_url

    def send(
        self,
        content: str,
        webhook_url: Optional[str] = None,
        file_path: Optional[str] = None,
        *,
        event_channel: bool = False,
    ) -> bool:
        """Send a Discord webhook or channel message.

        Parameters
        ----------
        content:
            Message text to send.
        webhook_url:
            Override webhook URL. If ``event_channel`` is ``True`` this is
            ignored.
        file_path:
            Optional path to an attachment.
        event_channel:
            If ``True`` and ``Config.EVENT_CHANNEL_ID`` is set, the
            message is posted via ``send_discord_message``.
        """

        if event_channel and Config.EVENT_CHANNEL_ID:
            try:
                send_discord_message(Config.EVENT_CHANNEL_ID, content, file_path)
                logging.info("📤 Event-Channel Nachricht gesendet")
                return True
            except Exception as e:  # pragma: no cover - network failure
                logging.error(f"❌ Fehler beim Channel-Senden: {e}")
                return False

        url = webhook_url or self.default_url
        if not url:
            logging.error("❌ Kein Webhook-URL angegeben")
            return False

        data = {"content": content}

        try:
            if file_path:
                with open(file_path, "rb") as fh:
                    response = requests.post(url, data=data, files={"file": fh})
            else:
                response = requests.post(url, data=data)
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
