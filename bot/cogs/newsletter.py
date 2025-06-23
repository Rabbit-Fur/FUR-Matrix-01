"""newsletter_cog.py – Slash-Command für Clan-Announcements."""

import logging

import discord
from discord import app_commands
from discord.ext import commands

from fur_lang.i18n import t
from mongo_service import get_collection

log = logging.getLogger(__name__)

ADMIN_ROLE_IDS = {"345678901234567890"}  # aus .env lesen, falls global benötigt


class Newsletter(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def user_is_admin(self, user: discord.User | discord.Member) -> bool:
        if isinstance(user, discord.Member):
            return (
                any(role.id in ADMIN_ROLE_IDS for role in user.roles)
                or user.guild_permissions.administrator
            )
        return False

    @app_commands.command(
        name=app_commands.locale_str("cmd_announce_name"),
        description=app_commands.locale_str("cmd_announce_desc"),
    )
    @app_commands.describe(message=app_commands.locale_str("cmd_announce_param_message_desc"))
    async def announce(self, interaction: discord.Interaction, message: str):
        user = interaction.user
        lang = "de"
        db_user = get_collection("users").find_one({"discord_id": str(user.id)})
        if db_user and "lang" in db_user:
            lang = db_user["lang"]

        if not self.user_is_admin(user):
            await interaction.response.send_message(
                t("announce_no_permission", lang=lang), ephemeral=True
            )
            return

        if not message.strip():
            await interaction.response.send_message(t("announce_usage", lang=lang), ephemeral=True)
            return

        try:
            await interaction.channel.send(t("announce_message", message=message, lang=lang))
            await interaction.response.send_message(
                t("announce_success", lang=lang), ephemeral=True
            )
            log.info(f"📢 Announcement von {user.display_name} in Channel {interaction.channel.id}")
        except discord.Forbidden:
            log.warning("Bot hat keine Berechtigung zum Senden in diesem Channel.")
            await interaction.response.send_message(
                t("announce_no_permission", lang=lang), ephemeral=True
            )
        except Exception as e:
            log.error(f"❌ Fehler beim Senden der Ankündigung: {e}", exc_info=True)
            await interaction.response.send_message(t("announce_error", lang=lang), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Newsletter(bot))
