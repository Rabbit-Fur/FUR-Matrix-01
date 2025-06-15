"""
reminders.py – Discord-Cog für wiederkehrende Erinnerungen (Events, Quests etc.)

Dieses Cog versendet regelmäßig Erinnerungsnachrichten an einen konfigurierbaren Kanal.
"""

import logging
from datetime import datetime

import discord
from discord.ext import commands, tasks

from config import Config

log = logging.getLogger(__name__)


class Reminders(commands.Cog):
    """
    Discord-Cog: Regelmäßige Erinnerungen für Events, Quests und mehr.

    - Nutzt Discord Tasks für zeitgesteuerte Benachrichtigungen.
    - Channel-ID wird aus der zentralen Config geladen.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_id = Config.REMINDER_CHANNEL_ID
        self.reminder_loop.start()
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_id = int(os.getenv("REMINDER_CHANNEL_ID", "1365580225945014385"))
        self.reminder_loop.start()

    def cog_unload(self):
        """Stoppt den Reminder-Loop beim Entladen des Cogs."""
        self.reminder_loop.cancel()

    @tasks.loop(minutes=60)
    async def reminder_loop(self):
        """Task: Sendet jede Stunde eine Erinnerungsnachricht in den Channel."""
        now = datetime.utcnow().strftime("%H:%M")
        channel = self.bot.get_channel(self.channel_id)
        if channel:
            try:
                await channel.send(f"⏰ Reminder Loop: UTC {now} – check your quests!")
                log.info(f"Reminder gesendet an Channel {self.channel_id} (UTC {now})")
            except Exception as e:
                log.error(f"Fehler beim Senden des Reminders: {e}")
        else:
            log.warning(f"Channel-ID {self.channel_id} nicht gefunden oder ungültig.")

    @reminder_loop.before_loop
    async def before_reminder(self):
        """Wartet bis Bot vollständig bereit ist, bevor der Loop startet."""
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    """Fügt das Reminders-Cog dem Bot hinzu (discord.py 2.x-Standard)."""
    await bot.add_cog(Reminders(bot))
