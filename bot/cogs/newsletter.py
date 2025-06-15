"""
newsletter.py – Discord-Cog für Clan-Newsletter & Ankündigungen

Erlaubt es Administratoren, wichtige Nachrichten als Clan-Announcements im Channel zu posten.
"""

import logging
import discord
from discord.ext import commands
from fur_lang.i18n import t

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
    async def announce(self, ctx: commands.Context, *, message: str = "") -> None:
        """
        Befehl: !announce <Nachricht>
        Sendet eine Clan-Ankündigung im aktuellen Channel.
        """
        lang = "de"  # 🔁 später dynamisch aus User-DB

        if not message.strip():
            await ctx.send(t("announce_usage", lang=lang))
            return

        try:
            announcement = t("announce_prefix", lang=lang) + "\n" + message
            await ctx.send(announcement)
            log.info(f"📢 Announcement von {ctx.author} in Channel {ctx.channel.id}")
        except discord.Forbidden:
            log.warning("Bot hat keine Berechtigung zum Senden in diesem Channel.")
            await ctx.send(t("announce_no_permission", lang=lang))
        except Exception as e:
            log.error(f"❌ Fehler beim Senden der Ankündigung: {e}", exc_info=True)
            await ctx.send(t("announce_error", lang=lang))


async def setup(bot: commands.Bot) -> None:
    """Registriert das Newsletter-Cog beim Bot."""
    await bot.add_cog(Newsletter(bot))
