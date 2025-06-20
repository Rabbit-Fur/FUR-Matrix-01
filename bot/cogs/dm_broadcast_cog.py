"""DM broadcast cog for FUR Discord bot."""

import asyncio
import logging
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from config import Config
from fur_lang.i18n import t

log = logging.getLogger(__name__)

MESSAGE_DELAY = 1.5
RATE_LIMIT_SECONDS = 60


class DMBroadcastCog(commands.Cog):
    """Allows admins to send a DM to all guild members."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.broadcast_lock = asyncio.Lock()
        self.last_used: dict[int, float] = {}

    def has_admin_role(self, member: discord.Member) -> bool:
        member_role_ids = {str(role.id) for role in member.roles}
        return bool(member_role_ids.intersection(Config.ADMIN_ROLE_IDS))

    @app_commands.command(name="dm_all", description="Broadcast a DM to all members")
    @app_commands.describe(text="Message to send (max 2000 characters)")
    async def dm_all(self, interaction: discord.Interaction, *, text: str) -> None:
        """Send a direct message to all reachable guild members."""
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(
                t("dm_broadcast_member_only", default="Command only for guild members."),
                ephemeral=True,
            )
            return

        if not self.has_admin_role(interaction.user):
            await interaction.response.send_message(
                t("dm_broadcast_no_permission", default="You lack permission."),
                ephemeral=True,
            )
            return

        if len(text) > 2000:
            await interaction.response.send_message(
                t(
                    "dm_broadcast_too_long",
                    default="Message too long (max 2000 characters).",
                ),
                ephemeral=True,
            )
            return

        now = datetime.utcnow().timestamp()
        if now - self.last_used.get(interaction.user.id, 0) < RATE_LIMIT_SECONDS:
            await interaction.response.send_message(
                t(
                    "dm_broadcast_rate_limit",
                    default="You can use this command only once per minute.",
                ),
                ephemeral=True,
            )
            return

        if self.broadcast_lock.locked():
            await interaction.response.send_message(
                t("dm_broadcast_running", default="A broadcast is already running."),
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)
        self.last_used[interaction.user.id] = now

        async with self.broadcast_lock:
            guild = self.bot.get_guild(Config.DISCORD_GUILD_ID)
            if not guild:
                await interaction.followup.send(
                    t("dm_broadcast_guild_missing", default="Guild not found."),
                    ephemeral=True,
                )
                return

            success_count = 0
            fail_count = 0
            for member in guild.members:
                if member.bot:
                    continue
                try:
                    await member.send(text)
                    success_count += 1
                except discord.Forbidden:
                    fail_count += 1
                    log.warning("\u26d4\ufe0f DM blocked for %s", member.id)
                except Exception as exc:  # pragma: no cover - network issues
                    fail_count += 1
                    log.error("Failed to DM %s: %s", member.id, exc)
                await asyncio.sleep(MESSAGE_DELAY)

            embed = discord.Embed(title="DM Broadcast")
            embed.add_field(
                name=t("dm_broadcast_sent", default="Gesendet"),
                value=str(success_count),
            )
            embed.add_field(
                name=t("dm_broadcast_failed", default="Blockiert"),
                value=str(fail_count),
            )
            await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    """Register the cog."""
    await bot.add_cog(DMBroadcastCog(bot))
