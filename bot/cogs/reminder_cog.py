"""MongoDB-based reminder cog."""

import logging
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

from database.mongo_client import db
from fur_lang.i18n import t

log = logging.getLogger(__name__)


class ReminderCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_reminders.start()

    def cog_unload(self) -> None:
        self.check_reminders.cancel()

    def get_user_language(self, user_id: int) -> str:
        user = db["users"].find_one({"discord_id": str(user_id)})
        return user.get("lang", "de") if user else "de"

    @tasks.loop(minutes=5.0)
    async def check_reminders(self) -> None:
        now = datetime.utcnow()
        window_start = now + timedelta(minutes=10)
        window_end = now + timedelta(minutes=15)

        try:
            events = db["events"].find(
                {"event_time": {"$gte": window_start, "$lte": window_end}}
            )
            for event in events:
                participants = db["participants"].find({"event_id": event["_id"]})
                for p in participants:
                    user_id = int(p["user_id"])
                    if db["reminders_sent"].find_one(
                        {"event_id": event["_id"], "user_id": user_id}
                    ):
                        continue
                    lang = self.get_user_language(user_id)
                    try:
                        user = self.bot.get_user(user_id) or await self.bot.fetch_user(
                            user_id
                        )
                        if not user:
                            log.warning(f"User ID {user_id} not found.")
                            continue
                        msg = t("reminder_event_15min", title=event["title"], lang=lang)
                        await user.send(msg)
                        db["reminders_sent"].insert_one(
                            {
                                "event_id": event["_id"],
                                "user_id": user_id,
                                "sent_at": now,
                            }
                        )
                        log.info(f"📤 15-Minuten-Reminder an {user_id} gesendet.")
                    except discord.Forbidden:
                        log.warning(f"🚫 DMs deaktiviert bei User {user_id}")
                    except Exception as e:
                        log.error(f"❌ Fehler beim Senden an {user_id}: {e}")
        except Exception as e:
            log.error(f"❌ Fehler beim Reminder-Check: {e}", exc_info=True)

    @check_reminders.before_loop
    async def before_check_reminders(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ReminderCog(bot))
