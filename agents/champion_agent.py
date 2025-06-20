"""ChampionAgent handles posters and Hall of Fame entries."""

from datetime import datetime

from .poster_agent import PosterAgent
from .webhook_agent import WebhookAgent


class ChampionAgent:
    def __init__(self, db, webhook: WebhookAgent | None = None):
        self.db = db
        self.webhook = webhook
        self.poster = PosterAgent()

    def announce_champion(self, username: str, month: str, stats: str = "") -> str:
        """Create poster, store entry and optionally send via webhook."""

        poster_path = self.poster.create_poster(username, stats)
        entry = {
            "username": username,
            "month": month,
            "poster_path": poster_path,
            "created_at": datetime.utcnow(),
        }
        self.db["hall_of_fame"].insert_one(entry)
        if self.webhook:
            self.webhook.send_champion_announcement(username, "PvP Champion", month, poster_path)
        return poster_path
