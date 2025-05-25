"""
leaderboard.py – Discord-Cog für Ingame-Statistiken und Rankings

Dieses Cog zeigt verschiedene Leaderboards (z.B. Raids, Donations) an.
Später kann es mit Datenbank- oder API-Anbindung erweitert werden.
"""

import logging
import discord
from discord.ext import commands

log = logging.getLogger(__name__)

class Leaderboard(commands.Cog):
    """
    Cog: Zeigt Ingame-Statistiken / Rankings an (aus DB/API).

    Der Befehl !top <Kategorie> zeigt ein Leaderboard für die gewünschte Kategorie.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="top")
    async def top_players(self, ctx: commands.Context, category: str = "raids") -> None:
        """
        Befehl: !top [Kategorie]
        Zeigt das Ranking der Top-Spieler in einer bestimmten Kategorie an.

        Args:
            ctx (commands.Context): Aufruf-Kontext.
            category (str, optional): Die Kategorie (Default: "raids").
        """
        # Platzhalter – später durch DB- oder API-Aufruf ersetzen!
        fake_data = {
            "raids": ["Alice - 120", "Bob - 110", "Charlie - 100"],
            "donations": ["Dino - 500", "Eva - 450"]
        }
        if category not in fake_data:
            await ctx.send(f"❌ Kategorie '{category}' ist nicht verfügbar.")
            log.warning(f"Leaderboard: Unbekannte Kategorie angefragt: {category}")
            return

        entries = fake_data[category]
        msg = f"🏆 Top {category.capitalize()}:\n" + "\n".join(entries)
        try:
            await ctx.send(msg)
            log.info(f"Leaderboard '{category}' an {ctx.channel.id} gesendet.")
        except Exception as e:
            log.error(f"Fehler beim Senden des Leaderboards: {e}", exc_info=True)

async def setup(bot: commands.Bot) -> None:
    """
    Registriert das Leaderboard-Cog beim Bot.

    Args:
        bot (commands.Bot): Discord-Bot-Instanz.
    """
    await bot.add_cog(Leaderboard(bot))
