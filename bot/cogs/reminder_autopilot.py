"""MongoDB based reminder autopilot cog."""

import logging
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

from database.mongo_client import db
from fur_lang.i18n import t

log = logging.getLogger(__name__)
REMINDER_INTERVAL_SECONDS = 60


class ReminderCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.reminder_loop.start()

    def cog_unload(self):
        self.reminder_loop.cancel()

    async def get_user_language(self, user_id: int) -> str:
        user = db["users"].find_one({"discord_id": str(user_id)})
        return user.get("lang", "de") if user else "de"

    @tasks.loop(seconds=REMINDER_INTERVAL_SECONDS)
    async def reminder_loop(self):
        await self.bot.wait_until_ready()
        now = datetime.utcnow()
        window_start = now + timedelta(minutes=5)
        window_end = now + timedelta(minutes=6)

        try:
            events = db["events"].find(
                {"event_time": {"$gte": window_start, "$lte": window_end}}
            )
            for event in events:
                participants = db["event_participants"].find({"event_id": event["_id"]})
                for p in participants:
                    user_id = int(p["user_id"])
                    if db["reminders_sent"].find_one(
                        {"event_id": event["_id"], "user_id": user_id}
                    ):
                        continue
                    lang = await self.get_user_language(user_id)
                    try:
                        user = await self.bot.fetch_user(user_id)
                        message = t(
                            "reminder_event_5min", title=event["title"], lang=lang
                        )
                        await user.send(message)
                        db["reminders_sent"].insert_one(
                            {
                                "event_id": event["_id"],
                                "user_id": user_id,
                                "sent_at": now,
                            }
                        )
                        log.info(f"📤 DM-Erinnerung an {user_id} ({lang}) gesendet.")
                    except Exception as e:
                        log.warning(f"❌ Konnte DM an {user_id} nicht senden: {e}")
        except Exception as e:
            log.error(f"❌ Fehler im Reminder-Loop: {e}", exc_info=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(ReminderCog(bot))
