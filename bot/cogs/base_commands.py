"""base_commands.py – Globale Slash-Commands für Basisfunktionen (Ping, FUR Info)."""

import discord
from discord import app_commands
from discord.ext import commands

from fur_lang.i18n import t
from mongo_service import get_collection


class BaseCommands(commands.Cog):
    """Stellt globale Slash-Befehle für alle Nutzer bereit."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_user_lang(self, user_id: int) -> str:
        user = get_collection("users").find_one({"discord_id": str(user_id)})
        return user.get("lang", "de") if user else "de"

    @app_commands.command(
        name=app_commands.locale_str("cmd_ping_name"),
        description=app_commands.locale_str("cmd_ping_desc"),
    )
    async def ping(self, interaction: discord.Interaction):
        lang = self.get_user_lang(interaction.user.id)
        await interaction.response.send_message(t("base_ping_pong", lang=lang), ephemeral=True)

    @app_commands.command(
        name=app_commands.locale_str("cmd_fur_name"),
        description=app_commands.locale_str("cmd_fur_desc"),
    )
    async def fur_info(self, interaction: discord.Interaction):
        lang = self.get_user_lang(interaction.user.id)
        await interaction.response.send_message(t("base_fur_info", lang=lang), ephemeral=False)


async def setup(bot: commands.Bot) -> None:
    """Registriert das BaseCommands-Cog beim Bot."""
    await bot.add_cog(BaseCommands(bot))
