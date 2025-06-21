"""reminder_optout_cog.py – Opt-out Reminder-System via Slash-Command & MongoDB."""

import logging

import discord
from discord import app_commands
from discord.ext import commands

from fur_lang.i18n import t
from mongo_service import get_collection

log = logging.getLogger(__name__)


class ReminderOptOut(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="reminder_stop", description="Deaktiviert Event-Reminder für dich.")
    async def reminder_stop(self, interaction: discord.Interaction):
        user = interaction.user
        discord_id = str(user.id)
        lang = "de"

        user_data = get_collection("users").find_one({"discord_id": discord_id})
        if user_data and "lang" in user_data:
            lang = user_data["lang"]

        try:
            get_collection("reminder_optout").update_one(
                {"discord_id": discord_id}, {"$set": {"discord_id": discord_id}}, upsert=True
            )
            log.info(f"🚫 Reminder deaktiviert für {discord_id}")
            await interaction.response.send_message(
                t("reminder_optout_success", lang=lang), ephemeral=True
            )
        except Exception as e:
            log.error(f"❌ Fehler beim Reminder-Opt-Out für {discord_id}: {e}")
            await interaction.response.send_message(
                t("reminder_optout_error", lang=lang), ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(ReminderOptOut(bot))
