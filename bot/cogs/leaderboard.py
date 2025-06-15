"""
leaderboard.py – Discord-Cog für Live-Rankings aus der Datenbank

Zeigt Top-Spieler in Kategorien wie Raids oder Donations aus der leaderboard-Tabelle.
"""

import logging
from discord.ext import commands
from web.database import get_db
from fur_lang.i18n import t

log = logging.getLogger(__name__)


class Leaderboard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="top")
    async def top_players(self, ctx: commands.Context, category: str = "raids") -> None:
        """
        Befehl: !top [Kategorie]
        Holt die Top 10 für eine Kategorie aus der Datenbank.
        """
        lang = "de"  # 🔁 später aus Nutzerprofil

        try:
            db = get_db()
            rows = db.execute(
                """
                SELECT username, score
                FROM leaderboard
                WHERE category = ?
                ORDER BY score DESC
                LIMIT 10
                """,
                (category.lower(),)
            ).fetchall()

            if not rows:
                await ctx.send(t("leaderboard_unknown_category", category=category, lang=lang))
                return

            header = t("leaderboard_header", category=category.capitalize(), lang=lang)
            content = "\n".join(
                [f"{i+1}. {row['username']} – {row['score']}" for i, row in enumerate(rows)]
            )

            await ctx.send(f"{header}\n{content}")
            log.info(f"📊 Live-Leaderboard '{category}' gesendet in {ctx.channel.id}")

        except Exception as e:
            log.error(f"❌ Fehler beim Leaderboard-Versand: {e}", exc_info=True)
            await ctx.send(t("leaderboard_error", lang=lang))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Leaderboard(bot))
