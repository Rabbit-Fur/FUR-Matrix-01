"""reminder_autopilot_cog.py – Reminder-Autopilot für Events (MongoDB-basiert)."""

import asyncio
import logging
import os
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks

from config import Config, is_production
from fur_lang.i18n import t
from mongo_service import get_collection
from utils import poster_generator
from utils.event_helpers import get_events_for, parse_event_time


def is_opted_out(user_id: int) -> bool:
    """Return True if the user opted out of reminders."""
    uid = str(user_id)
    if get_collection("reminder_optout").find_one({"discord_id": uid}):
        return True
    settings = get_collection("user_settings").find_one(
        {"discord_id": uid, "reminder_optout": True}
    )
    return bool(settings)


log = logging.getLogger(__name__)
REMINDER_INTERVAL_SECONDS = 60


def should_send_daily(dt: datetime) -> bool:
    """Return True when a daily poster should be sent."""
    return dt.hour == 8


def should_send_weekly(dt: datetime) -> bool:
    """Return True when a weekly poster should be sent."""
    return dt.weekday() == 6 and dt.hour == 12


class ReminderAutopilot(commands.Cog):
    """
    Reminder autopilot: sends automatic event reminders via DM.

    – Uses `events`, `event_participants`, `reminders_sent` from MongoDB
    – Sends 10‑minute reminders to all participants
    – Language per user via the user collection
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.delay = float(os.getenv("REMINDER_DM_DELAY", "1"))
        self.reminder_loop.start()
        self.daily_poster_loop.start()
        self.weekly_poster_loop.start()

    def cog_unload(self):
        self.reminder_loop.cancel()
        self.daily_poster_loop.cancel()
        self.weekly_poster_loop.cancel()

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
        if not is_production():
            log.info("DM skipped in dev mode")
            return

        now = datetime.utcnow()
        window_start = now + timedelta(minutes=10)
        window_end = now + timedelta(minutes=11)

        try:
            today_events = get_events_for(now)
            events = [
                ev
                for ev in today_events
                if (
                    (ev_time := parse_event_time(ev.get("event_time")))
                    and window_start <= ev_time <= window_end
                )
            ]
            for event in events:
                participants = get_collection("event_participants").find({"event_id": event["_id"]})
                for p in participants:
                    user_id = int(p["user_id"])

                    if get_collection("reminders_sent").find_one(
                        {"event_id": event["_id"], "user_id": user_id}
                    ):
                        continue

                    if is_opted_out(user_id):
                        continue

                    lang = await self.get_user_language(user_id)
                    try:
                        user = await self.bot.fetch_user(user_id)
                        if not user:
                            log.warning(f"❌ User-ID {user_id} nicht gefunden.")
                            continue

                        message = t("reminder_event_10min", title=event["title"], lang=lang)
                        mention = (
                            f"<@&{Config.REMINDER_ROLE_ID}> "
                            if getattr(Config, "REMINDER_ROLE_ID", 0)
                            else ""
                        )
                        await user.send(f"{mention}{message}" if mention else message)
                        get_collection("reminders_sent").insert_one(
                            {"event_id": event["_id"], "user_id": user_id, "sent_at": now}
                        )
                        log.info(f"📤 10-Minuten-DM an {user_id} ({lang}) gesendet.")
                    except discord.Forbidden:
                        log.warning(f"🚫 DMs deaktiviert bei {user_id}")
                    except Exception as e:
                        log.warning(f"❌ Fehler bei DM an {user_id}: {e}")
        except Exception as e:
            log.error(f"❌ Reminder-Autopilot-Fehler: {e}", exc_info=True)

    async def _build_daily_lines(self) -> list[str]:
        now = datetime.utcnow()
        tomorrow = now + timedelta(days=1)
        events = (
            get_collection("events")
            .find({"event_time": {"$gte": now, "$lte": tomorrow}}, {"title": 1, "event_time": 1})
            .sort("event_time", 1)
        )
        lines: list[str] = []
        for ev in events:
            dt = parse_event_time(ev.get("event_time"))
            if dt:
                lines.append(f"{dt.strftime('%d.%m %H:%M')} - {ev['title']}")
        if not lines:
            lines.append("No events today.")
        return lines

    async def _build_weekly_lines(self) -> list[str]:
        now = datetime.utcnow()
        week = now + timedelta(days=7)
        lines: list[str] = []
        events = (
            get_collection("events")
            .find({"event_time": {"$gte": now, "$lte": week}}, {"title": 1, "event_time": 1})
            .sort("event_time", 1)
        )
        for ev in events:
            dt = parse_event_time(ev.get("event_time"))
            if dt:
                lines.append(f"{dt.strftime('%d.%m %H:%M')} - {ev['title']}")
        if not lines:
            lines.append("No upcoming events.")
        return lines

    async def _send_poster_to_members(self, poster_path: str) -> None:
        guild = self.bot.get_guild(Config.DISCORD_GUILD_ID)
        if not guild:
            log.warning("Guild not found for poster dispatch")
            return
        for member in guild.members:
            if member.bot:
                continue
            if is_opted_out(member.id):
                continue
            try:
                file = discord.File(poster_path)
                await member.send(file=file)
                await asyncio.sleep(self.delay)
            except discord.Forbidden:
                log.warning("DM blocked for %s", member.id)
            except Exception as exc:  # noqa: BLE001
                log.warning("Poster DM error for %s: %s", member.id, exc)

    async def send_daily_poster(self) -> None:
        lines = await self._build_daily_lines()
        path = poster_generator.generate_text_poster("Today's Events", lines)
        await self._send_poster_to_members(path)

    async def send_weekly_poster(self) -> None:
        lines = await self._build_weekly_lines()
        path = poster_generator.generate_text_poster("Events This Week", lines)
        await self._send_poster_to_members(path)

    @tasks.loop(hours=1)
    async def daily_poster_loop(self):
        await self.bot.wait_until_ready()
        if not is_production():
            return
        now = datetime.utcnow()
        if should_send_daily(now):
            await self.send_daily_poster()

    @tasks.loop(hours=1)
    async def weekly_poster_loop(self):
        await self.bot.wait_until_ready()
        if not is_production():
            return
        now = datetime.utcnow()
        if should_send_weekly(now):
            await self.send_weekly_poster()

    #
    # 🔧 Slash-Command für manuellen Trigger (Admin)
    #

    @app_commands.command(
        name=app_commands.locale_str("cmd_reminder_autopilot_now_name"),
        description=app_commands.locale_str("cmd_reminder_autopilot_now_desc"),
    )
    async def reminder_autopilot_now(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(t("no_admin_rights"), ephemeral=True)
            return

        await self.run_reminder_check()
        await interaction.response.send_message(t("reminder_autopilot_run"), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(ReminderAutopilot(bot))
