"""
reminders.py – Discord-Cog für wiederkehrende Erinnerungen (Events, Quests etc.)

Dieses Cog versendet stündlich eine Erinnerungsnachricht an den Reminder-Channel.
"""

import logging
import os
from datetime import datetime

import discord
from discord.ext import commands, tasks

from config import Config
from fur_lang.i18n import t

log = logging.getLogger(__name__)


class Reminders(commands.Cog):
    """
    Discord-Cog: Regelmäßige Erinnerungen für Quests, Events und tägliche Aufgaben.

    - Channel-ID kommt aus Umgebungsvariable oder Fallback `Config.REMINDER_CHANNEL_ID`
    - Nachricht ist mehrsprachig via t()
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_id = int(
            os.getenv("REMINDER_CHANNEL_ID", getattr(Config, "REMINDER_CHANNEL_ID", 0))
        )
        self.reminder_loop.start()

    def cog_unload(self):
        """Stoppt den Reminder-Loop beim Entladen des Cogs."""
        self.reminder_loop.cancel()

    @tasks.loop(minutes=60)
    async def reminder_loop(self):
        """
        Task: Sendet jede Stunde eine Erinnerungsnachricht in den Reminder-Channel.
        """
        now = datetime.utcnow().strftime("%H:%M")
        channel = self.bot.get_channel(self.channel_id)

        if channel:
            try:
                message = t(
                    "reminder_hourly", time=now, lang="de"
                )  # 🔁 später dynamisch
                await channel.send(message)
                log.info(
                    f"📤 Reminder gesendet an Channel {self.channel_id} (UTC {now})"
                )
            except Exception as e:
                log.error(f"❌ Fehler beim Senden des stündlichen Reminders: {e}")
        else:
            log.warning(
                f"⚠️ Channel-ID {self.channel_id} ungültig oder nicht auffindbar."
            )

    @reminder_loop.before_loop
    async def before_reminder(self):
        """Wartet bis der Bot bereit ist, bevor der Reminder-Loop startet."""
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    """Registriert das Reminders-Cog beim Bot."""
    await bot.add_cog(Reminders(bot))
