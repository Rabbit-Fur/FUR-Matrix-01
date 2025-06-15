"""
leaderboard.py – Discord-Cog für Ingame-Statistiken und Rankings

Dieses Cog zeigt verschiedene Leaderboards (z. B. Raids, Donations) an.
Später kann es mit Datenbank- oder API-Anbindung erweitert werden.
"""

import logging

import discord
from discord.ext import commands
from fur_lang.i18n import t

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
        """
        lang = "de"  # 🔁 später automatisch aus DB/User

        # 🔁 Platzhalterdaten – später durch DB/API ersetzen
        fake_data = {
            "raids": ["Alice – 120", "Bob – 110", "Charlie – 100"],
            "donations": ["Dino – 500", "Eva – 450"],
        }

        if category not in fake_data:
            await ctx.send(t("leaderboard_unknown_category", category=category, lang=lang))
            log.warning(f"❌ Unbekannte Kategorie: {category}")
            return

        entries = fake_data[category]
        leaderboard_text = "\n".join(entries)
        header = t("leaderboard_header", category=category.capitalize(), lang=lang)

        try:
            await ctx.send(f"{header}\n{leaderboard_text}")
            log.info(f"📊 Leaderboard '{category}' gesendet in {ctx.channel.id}")
        except Exception as e:
            log.error(f"❌ Fehler beim Leaderboard-Versand: {e}", exc_info=True)


async def setup(bot: commands.Bot) -> None:
    """Registriert das Leaderboard-Cog beim Bot."""
    await bot.add_cog(Leaderboard(bot))
