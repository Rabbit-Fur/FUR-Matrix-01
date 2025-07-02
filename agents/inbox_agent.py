"""Simple inbox handler for Discord DMs and feedback messages."""

from datetime import datetime


class InboxAgent:
    def __init__(self, db):
        self.db = db

    def receive_message(self, discord_id: str, content: str):
        self.db["inbox"].insert_one(
            {
                "discord_id": discord_id,
                "message": content,
                "timestamp": datetime.utcnow(),
            }
        )
        return "📥 Nachricht empfangen – danke für dein Feedback!"
