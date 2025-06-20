import asyncio
import logging

from bson import ObjectId

from bot.bot_main import bot
from mongo_service import get_collection


async def _send_reminder(reminder_id: str) -> None:
    reminder = get_collection("reminders").find_one({"_id": ObjectId(reminder_id)})
    if not reminder:
        logging.warning("Reminder-ID %s not found", reminder_id)
        return

    participants = get_collection("reminder_participants").find({"reminder_id": reminder_id})

    for row in participants:
        try:
            user = await bot.fetch_user(int(row["discord_id"]))
            if user:
                await user.send(reminder["message"])
                logging.info("[Reminder] Sent to %s", user)
        except Exception as exc:  # pragma: no cover - network issues
            logging.error("[Reminder] Failed to send to %s: %s", row["discord_id"], exc)


def send_reminder_by_id(reminder_id: str) -> None:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(_send_reminder(reminder_id))
    else:
        loop.run_until_complete(_send_reminder(reminder_id))
