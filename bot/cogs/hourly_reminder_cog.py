import logging
from datetime import datetime, timedelta
from typing import Dict

import discord
from discord.ext import commands, tasks

from config import Config
from fur_lang.i18n import t
from mongo_service import get_collection

log = logging.getLogger(__name__)


def get_open_tasks(channel_id: int) -> int:
    """Return the number of open tasks for a channel."""
    try:
        collection = get_collection("tasks")
        return collection.count_documents({"channel_id": channel_id, "status": "open"})
    except Exception:
        log.warning("tasks collection missing or inaccessible")
        return 0


class HourlyReminderCog(commands.Cog):
    """Send hourly task reminders in a public channel."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_sent: Dict[int, datetime] = {}
        self.reminder_loop.start()

    def cog_unload(self) -> None:
        self.reminder_loop.cancel()

    @tasks.loop(minutes=1)
    async def reminder_loop(self) -> None:
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(Config.REMINDER_CHANNEL_ID)
        if not channel:
            log.warning("Reminder channel not found")
            return

        now = datetime.utcnow()
        last = self._last_sent.get(channel.id)
        if last and now - last < timedelta(hours=1):
            return

        if get_open_tasks(channel.id) <= 0:
            return

        msg = t("reminder_hourly", lang="en", time=now.strftime("%H:%M"))
        try:
            await channel.send(msg)
            self._last_sent[channel.id] = now
        except discord.DiscordException as exc:  # noqa: BLE001
            log.error("Failed to send reminder: %s", exc)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HourlyReminderCog(bot))
