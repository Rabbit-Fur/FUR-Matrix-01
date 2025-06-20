"""ReminderAgent schedules and dispatches Discord reminders."""

from datetime import datetime
from typing import Any


class ReminderAgent:
    def __init__(self, db):
        self.db = db
        self.reminders = db["reminders"]
        self.opt_out = db["reminder_opt_out"]

    def schedule(self, user_id: int, message: str, remind_at: datetime) -> None:
        """Store a reminder in the database."""

        self.reminders.insert_one(
            {"user_id": user_id, "message": message, "remind_at": remind_at, "sent": False}
        )

    async def dispatch_due(self, bot: Any) -> int:
        """Send due reminders via the Discord bot."""

        now = datetime.utcnow()
        to_send = list(self.reminders.find({"remind_at": {"$lte": now}, "sent": False}))
        count = 0
        for entry in to_send:
            if self.opt_out.find_one({"user_id": entry["user_id"]}):
                continue
            try:
                user = await bot.fetch_user(int(entry["user_id"]))
                await user.send(entry["message"])
                self.reminders.update_one(
                    {"_id": entry["_id"]}, {"$set": {"sent": True, "sent_at": now}}
                )
                count += 1
            except Exception:
                pass
        return count

    def opt_out_user(self, discord_id: int) -> None:
        """Add a user to the opt-out list."""

        self.opt_out.update_one(
            {"user_id": discord_id}, {"$set": {"user_id": discord_id}}, upsert=True
        )
