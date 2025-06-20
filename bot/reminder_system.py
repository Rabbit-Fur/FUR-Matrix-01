"""reminder_sender.py – Reminder-Versand via MongoDB & Discord DM."""

import asyncio
import logging
from typing import Optional

from bson import ObjectId

from bot.bot_main import bot
from mongo_service import get_collection

log = logging.getLogger(__name__)


async def _send_reminder(reminder_id: str) -> Optional[int]:
    """Sendet einen Reminder an alle zugehörigen Teilnehmer (per DM)."""
    try:
        reminder = get_collection("reminders").find_one({"_id": ObjectId(reminder_id)})
        if not reminder:
            log.warning("❗ Reminder-ID %s nicht gefunden", reminder_id)
            return None

        participants = get_collection("reminder_participants").find({"reminder_id": reminder_id})
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
