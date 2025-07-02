"""reminder_sender.py – Reminder-Versand via MongoDB & Discord DM."""

import asyncio
import logging
from typing import Optional

from bson import ObjectId

from bot.bot_main import bot
from config import Config
from motor.motor_asyncio import AsyncIOMotorClient

# use motor client for non-blocking mongodb access
client = AsyncIOMotorClient(Config.MONGODB_URI or "mongodb://localhost:27017/furdb")
db = client.get_default_database()
reminders_col = db["reminders"]
participants_col = db["reminder_participants"]

log = logging.getLogger(__name__)


async def _send_reminder(reminder_id: str) -> Optional[int]:
    """Sendet einen Reminder an alle zugehörigen Teilnehmer (per DM)."""
    try:
        reminder = await reminders_col.find_one({"_id": ObjectId(reminder_id)})
        if not reminder:
            log.warning("❗ Reminder-ID %s nicht gefunden", reminder_id)
            return None

        cursor = participants_col.find({"reminder_id": reminder_id})
        participants = await cursor.to_list(length=None)
        success_count = 0
        for row in participants:
            try:
                user = await bot.fetch_user(int(row["discord_id"]))
                if user:
                    await user.send(reminder["message"])
                    log.info("📤 Reminder an %s gesendet", user)
                    success_count += 1
            except Exception as exc:
                log.error("❌ Fehler beim Senden an %s: %s", row["discord_id"], exc)

        return success_count
    except Exception as e:
        log.error("❌ Reminder-Fehler bei Versand: %s", e, exc_info=True)
        return None


def send_reminder_by_id(reminder_id: str) -> Optional[int]:
    """Entry-Point für Web/API – Reminder-Versand synchron oder async."""
    loop = asyncio.get_event_loop()
    if loop.is_running():
        return asyncio.ensure_future(_send_reminder(reminder_id))  # for in-app use
    else:
        return loop.run_until_complete(_send_reminder(reminder_id))
