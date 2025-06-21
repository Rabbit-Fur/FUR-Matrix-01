"""dm_broadcast_cog.py – Slash-Command für DM-Broadcasts an alle Mitglieder."""

import asyncio
import logging
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from config import Config
from fur_lang.i18n import t

log = logging.getLogger(__name__)

MESSAGE_DELAY = 1.5  # Sekunden zwischen DMs (Vermeidung von Ratelimits)
RATE_LIMIT_SECONDS = 60  # 1 Broadcast pro Minute pro User


class DMBroadcastCog(commands.Cog):
    """Admin-Slash-Command: Direktnachricht an alle Server-Mitglieder."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.broadcast_lock = asyncio.Lock()
        self.last_used: dict[int, float] = {}

    def has_admin_role(self, member: discord.Member) -> bool:
        """Prüft, ob der Nutzer eine ADMIN-Rolle hat."""
        member_role_ids = {str(role.id) for role in member.roles}
        return bool(member_role_ids.intersection(Config.ADMIN_ROLE_IDS))

    @app_commands.command(
        name="dm_all", description="Sende eine Nachricht an alle Mitglieder per DM."
    )
    @app_commands.describe(text="Nachricht (max 2000 Zeichen)")
    async def dm_all(self, interaction: discord.Interaction, *, text: str) -> None:
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(
                t("dm_broadcast_member_only", default="Nur für Mitglieder verfügbar."),
                ephemeral=True,
            )
            return

        if not self.has_admin_role(interaction.user):
            await interaction.response.send_message(
                t("dm_broadcast_no_permission", default="Du hast keine Berechtigung."),
                ephemeral=True,
            )
            return

        if len(text) > 2000:
            await interaction.response.send_message(
                t("dm_broadcast_too_long", default="Nachricht zu lang (max. 2000 Zeichen)."),
                ephemeral=True,
            )
            return

        now = datetime.utcnow().timestamp()
        if now - self.last_used.get(interaction.user.id, 0) < RATE_LIMIT_SECONDS:
            await interaction.response.send_message(
                t("dm_broadcast_rate_limit", default="Nur 1 Broadcast pro Minute erlaubt."),
                ephemeral=True,
            )
            return

        if self.broadcast_lock.locked():
            await interaction.response.send_message(
                t("dm_broadcast_running", default="Ein Broadcast läuft bereits."),
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)
        self.last_used[interaction.user.id] = now

        async with self.broadcast_lock:
            guild = self.bot.get_guild(Config.DISCORD_GUILD_ID)
            if not guild:
                await interaction.followup.send(
                    t("dm_broadcast_guild_missing", default="Server nicht gefunden."),
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
                    log.warning("🚫 DM blockiert für %s", member.id)
                except Exception as exc:
                    fail_count += 1
                    log.error("❌ Fehler bei DM an %s: %s", member.id, exc)
                await asyncio.sleep(MESSAGE_DELAY)

            embed = discord.Embed(title="📢 DM Broadcast Ergebnis", color=discord.Color.blue())
            embed.add_field(
                name=t("dm_broadcast_sent", default="✅ Gesendet"), value=str(success_count)
            )
            embed.add_field(
                name=t("dm_broadcast_failed", default="❌ Fehlgeschlagen"), value=str(fail_count)
            )
            await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    """Registriert das Broadcast-Cog beim Bot."""
    await bot.add_cog(DMBroadcastCog(bot))
