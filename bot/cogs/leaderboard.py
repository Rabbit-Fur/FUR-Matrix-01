"""Leaderboard cog using MongoDB."""

import logging

from discord.ext import commands

from fur_lang.i18n import t
from mongo_service import get_collection

log = logging.getLogger(__name__)


class Leaderboard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="top")
    async def top_players(self, ctx: commands.Context, category: str = "raids") -> None:
        lang = "de"
        try:
            collection = get_collection("leaderboard")
            rows = collection.find({"category": category.lower()}).sort("score", -1).limit(10)
            rows = list(rows)
            if not rows:
                await ctx.send(t("leaderboard_unknown_category", category=category, lang=lang))
                return
            header = t("leaderboard_header", category=category.capitalize(), lang=lang)
            content = "\n".join(
                [f"{i+1}. {row['username']} – {row['score']}" for i, row in enumerate(rows)]
            )
            await ctx.send(t("leaderboard_message", header=header, content=content, lang=lang))
            log.info(f"📊 Live-Leaderboard '{category}' gesendet in {ctx.channel.id}")
        except Exception as e:
            log.error(f"❌ Fehler beim Leaderboard-Versand: {e}", exc_info=True)
            await ctx.send(t("leaderboard_error", lang=lang))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Leaderboard(bot))
