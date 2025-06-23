"""Leaderboard Cog – Slash-Command-Version mit MongoDB."""

import logging

import discord
from discord import app_commands
from discord.ext import commands

from fur_lang.i18n import t
from mongo_service import get_collection

log = logging.getLogger(__name__)


class Leaderboard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name=app_commands.locale_str("cmd_top_name"),
        description=app_commands.locale_str("cmd_top_desc"),
    )
    @app_commands.describe(category=app_commands.locale_str("cmd_top_param_category_desc"))
    async def top_players(self, interaction: discord.Interaction, category: str = "raids"):
        user_id = interaction.user.id
        lang = "de"
        user = get_collection("users").find_one({"discord_id": str(user_id)})
        if user and "lang" in user:
            lang = user["lang"]

        try:
            collection = get_collection("leaderboard")
            rows = collection.find({"category": category.lower()}).sort("score", -1).limit(10)
            rows = list(rows)

            if not rows:
                await interaction.response.send_message(
                    t("leaderboard_unknown_category", category=category, lang=lang), ephemeral=True
                )
                return

            header = t("leaderboard_header", category=category.capitalize(), lang=lang)
            content = "\n".join(
                [f"{i+1}. {row['username']} – {row['score']}" for i, row in enumerate(rows)]
            )
            result = t("leaderboard_message", header=header, content=content, lang=lang)
            await interaction.response.send_message(result)
            log.info(
                f"📊 Slash-Leaderboard '{category}' gesendet an {interaction.user.display_name}"
            )

        except Exception as e:
            log.error(f"❌ Fehler beim Leaderboard-Aufruf: {e}", exc_info=True)
            await interaction.response.send_message(
                t("leaderboard_error", lang=lang), ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Leaderboard(bot))
