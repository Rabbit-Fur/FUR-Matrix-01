"""
newsletter.py – Discord-Cog für Clan-Newsletter & Ankündigungen

Erlaubt es Administratoren, wichtige Nachrichten als Clan-Announcements im Channel zu posten.
"""

import logging

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


class Newsletter(commands.Cog):
    """
    Cog: Verwaltet Clan-Mitteilungen oder wichtige Ankündigungen.

    Nur Administratoren können die !announce-Funktion nutzen.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="announce")
    @commands.has_permissions(administrator=True)
    async def announce(self, ctx: commands.Context, *, message: str) -> None:
        """
        Befehl: !announce <Nachricht>
        Sendet eine Clan-Ankündigung im aktuellen Channel.

        Args:
            ctx (commands.Context): Aufruf-Kontext.
            message (str): Die Ankündigung.
        """
        try:
            await ctx.send(f"📢 Clan-Ankündigung:\n{message}")
            log.info(
                f"Announcement gesendet von {ctx.author} in Channel {ctx.channel.id}"
            )
        except discord.Forbidden:
            log.warning("Bot hat keine Berechtigung zum Senden in diesem Channel.")
        except Exception as e:
            log.error(f"Fehler beim Senden der Ankündigung: {e}", exc_info=True)


async def setup(bot: commands.Bot) -> None:
    """
    Registriert das Newsletter-Cog beim Bot.

    Args:
        bot (commands.Bot): Discord-Bot-Instanz.
    """
    await bot.add_cog(Newsletter(bot))
