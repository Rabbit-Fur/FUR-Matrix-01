import logging
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

from database.mongo_client import db

log = logging.getLogger(__name__)
REMINDER_INTERVAL_SECONDS = 60


class ReminderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminder_loop.start()

    def cog_unload(self):
        self.reminder_loop.cancel()

    @tasks.loop(seconds=REMINDER_INTERVAL_SECONDS)
    async def reminder_loop(self):
        await self.bot.wait_until_ready()
        now = datetime.utcnow()
        window_start = now + timedelta(minutes=5)
        window_end = now + timedelta(minutes=6)

        try:
            events = db["events"].find(
                {
                    "event_time": {
                        "$gte": window_start,
                        "$lte": window_end,
                    }
                }
            )
            for event in events:
                participants = db["event_participants"].find({"event_id": event["_id"]})
                for p in participants:
                    user_id = int(p["user_id"])
                    already_sent = db["reminders_sent"].find_one(
                        {"event_id": event["_id"], "user_id": user_id}
                    )
                    if already_sent:
                        continue
                    try:
                        user = await self.bot.fetch_user(user_id)
                        await user.send(
                            f"⏰ Reminder: Das Event **{event['title']}** beginnt in ca. 5 Minuten!"
                        )
                        db["reminders_sent"].insert_one(
                            {
                                "event_id": event["_id"],
                                "user_id": user_id,
                                "sent_at": now,
                            }
                        )
                    except Exception as e:
                        log.warning(f"❌ Konnte DM an {user_id} nicht senden: {e}")
        except Exception as e:
            log.error(f"❌ Fehler im Reminder-Loop: {e}", exc_info=True)


async def setup(bot):
    await bot.add_cog(ReminderCog(bot))
