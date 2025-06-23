import logging

import discord
from discord import app_commands
from discord.ext import commands

from fur_lang.i18n import t

log = logging.getLogger(__name__)


class ErrorHandler(commands.Cog):
    """Global application command error handler."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _reply(self, interaction: discord.Interaction, message: str) -> None:
        """Send a response or followup depending on state."""
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

    @commands.Cog.listener()
    async def on_application_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        """Handle slash command errors with localized messages."""
        lang = "de"
        if isinstance(error, commands.MissingPermissions):
            await self._reply(
                interaction,
                t("error_missing_permissions", default="🚫 Missing permissions.", lang=lang),
            )
        elif isinstance(error, commands.CommandOnCooldown):
            await self._reply(
                interaction,
                t("error_command_cooldown", default="⏱ Command is on cooldown.", lang=lang),
            )
        elif isinstance(error, commands.CommandInvokeError):
            log.error("CommandInvokeError: %s", error, exc_info=True)
            await self._reply(
                interaction,
                t("error_default_message", default="An error occurred.", lang=lang),
            )
        elif isinstance(error, commands.CheckFailure):
            await self._reply(
                interaction,
                t("error_check_failure", default="You cannot use this command.", lang=lang),
            )
        else:
            log.error("Unhandled command error: %s", error, exc_info=True)
            await self._reply(
                interaction,
                t("error_default_message", default="An error occurred.", lang=lang),
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ErrorHandler(bot))
