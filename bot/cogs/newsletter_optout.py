"""newsletter_optout.py - Opt-out for newsletter via Slash-Command."""

from __future__ import annotations

import logging

import discord
from discord import app_commands
from discord.ext import commands

from fur_lang.i18n import t
from mongo_service import get_collection

log = logging.getLogger(__name__)


class NewsletterOptOut(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name=app_commands.locale_str("cmd_newsletter_stop_name"),
        description=app_commands.locale_str("cmd_newsletter_stop_desc"),
    )
    async def newsletter_stop(self, interaction: discord.Interaction):
        user = interaction.user
        discord_id = str(user.id)
        lang = "de"

        user_data = get_collection("users").find_one({"discord_id": discord_id})
        if user_data and "lang" in user_data:
            lang = user_data["lang"]

        try:
            get_collection("newsletter_optout").update_one(
                {"discord_id": discord_id},
                {"$set": {"discord_id": discord_id}},
                upsert=True,
            )
            log.info("🚫 Newsletter deaktiviert für %s", discord_id)
            await interaction.response.send_message(
                t("newsletter_optout_success", lang=lang), ephemeral=True
            )
        except Exception as e:  # noqa: BLE001
            log.error("❌ Fehler beim Newsletter-Opt-Out für %s: %s", discord_id, e)
            await interaction.response.send_message(
                t("newsletter_optout_error", lang=lang), ephemeral=True
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(NewsletterOptOut(bot))
