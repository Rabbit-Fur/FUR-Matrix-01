"""reminder_autopilot_cog.py – Reminder-Autopilot für Events (MongoDB-basiert)."""

import logging
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks

from fur_lang.i18n import t
from mongo_service import get_collection

log = logging.getLogger(__name__)
REMINDER_INTERVAL_SECONDS = 60


class ReminderAutopilot(commands.Cog):
    """
    Reminder-Autopilot: Versendet automatisch 5-Minuten-DMs für Events.

    – Nutzt `events`, `event_participants`, `reminders_sent` aus MongoDB
    – Sprache pro User dynamisch aus der User-Collection
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.reminder_loop.start()

    def cog_unload(self):
        self.reminder_loop.cancel()

    async def get_user_language(self, user_id: int) -> str:
        user = get_collection("users").find_one({"discord_id": str(user_id)})
        return user.get("lang", "de") if user else "de"

    @tasks.loop(seconds=REMINDER_INTERVAL_SECONDS)
    async def reminder_loop(self):
        await self.bot.wait_until_ready()
        await self.run_reminder_check()

    @reminder_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    async def run_reminder_check(self):
        now = datetime.utcnow()
        window_start = now + timedelta(minutes=5)
        window_end = now + timedelta(minutes=6)

        try:
            events = get_collection("events").find(
                {"event_time": {"$gte": window_start, "$lte": window_end}}
            )
            for event in events:
                participants = get_collection("event_participants").find({"event_id": event["_id"]})
                for p in participants:
                    user_id = int(p["user_id"])

                    if get_collection("reminders_sent").find_one(
                        {"event_id": event["_id"], "user_id": user_id}
                    ):
                        continue

                    lang = await self.get_user_language(user_id)
                    try:
                        user = await self.bot.fetch_user(user_id)
                        if not user:
                            log.warning(f"❌ User-ID {user_id} nicht gefunden.")
                            continue

                        message = t("reminder_event_5min", title=event["title"], lang=lang)
                        await user.send(message)
                        get_collection("reminders_sent").insert_one(
                            {"event_id": event["_id"], "user_id": user_id, "sent_at": now}
                        )
                        log.info(f"📤 DM-Erinnerung an {user_id} ({lang}) gesendet.")
                    except discord.Forbidden:
                        log.warning(f"🚫 DMs deaktiviert bei {user_id}")
                    except Exception as e:
                        log.warning(f"❌ Fehler bei DM an {user_id}: {e}")
        except Exception as e:
            log.error(f"❌ Reminder-Autopilot-Fehler: {e}", exc_info=True)

    #
    # 🔧 Slash-Command für manuellen Trigger (Admin)
    #

    @app_commands.command(
        name="reminder_autopilot_now", description="Manuelles Auslösen des Reminder-Autopiloten."
    )
    async def reminder_autopilot_now(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("🚫 Keine Adminrechte.", ephemeral=True)
            return

        await self.run_reminder_check()
        await interaction.response.send_message(
            "✅ Reminder-Autopilot wurde manuell ausgeführt.", ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ReminderAutopilot(bot))
