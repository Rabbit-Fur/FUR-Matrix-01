"""Auto-send weekly newsletter DMs with upcoming events."""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks

from config import Config
from mongo_service import get_collection
from utils.event_helpers import format_events, get_events_for

log = logging.getLogger(__name__)


def should_send_newsletter(dt: datetime) -> bool:
    """Return True when newsletter should be dispatched."""
    return dt.weekday() == 6 and dt.hour == 12


class NewsletterAutopilot(commands.Cog):
    """Loop-based newsletter dispatcher."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.sent = 0
        self.blocked = 0
        self.errors = 0
        self.delay = float(os.getenv("NEWSLETTER_DM_DELAY", "1"))
        self.enabled = os.getenv("ENABLE_NEWSLETTER_AUTOPILOT", "true").lower() == "true"
        self.newsletter_loop.start()

    def cog_unload(self) -> None:
        self.newsletter_loop.cancel()

    @tasks.loop(hours=1)
    async def newsletter_loop(self) -> None:
        await self.bot.wait_until_ready()
        if not self.enabled:
            return
        now = datetime.utcnow()
        if should_send_newsletter(now):
            await self.send_newsletters()

    async def build_content(self) -> str:
        now = datetime.utcnow()
        events: list[dict] = []
        for i in range(7):
            events.extend(get_events_for(now + timedelta(days=i)))

        lines = ["📰 Upcoming Events"]
        if events:
            lines.append(format_events(events))
        else:
            lines.append("Keine Events in den nächsten 7 Tagen.")

        return "\n".join(lines)

    async def send_newsletters(self) -> None:
        guild = self.bot.get_guild(Config.DISCORD_GUILD_ID)
        if not guild:
            log.warning("Guild not found for newsletter dispatch")
            return
        content = await self.build_content()
        for member in guild.members:
            if member.bot:
                continue
            if get_collection("newsletter_optout").find_one({"discord_id": str(member.id)}):
                self.blocked += 1
                continue
            try:
                await member.send(content)
                self.sent += 1
            except discord.Forbidden:
                self.blocked += 1
                log.warning("DM blocked for %s", member.id)
            except Exception as exc:  # noqa: BLE001
                self.errors += 1
                log.error("Error sending newsletter to %s: %s", member.id, exc)
            await asyncio.sleep(self.delay)

    @app_commands.command(name="newsletter_now", description="Send newsletter immediately")
    async def newsletter_now(self, interaction: discord.Interaction) -> None:
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("🚫 Keine Adminrechte.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        await self.send_newsletters()
        await interaction.followup.send(
            f"Newsletter sent: {self.sent} ✅ / {self.blocked} 🚫 / {self.errors} ❌",
            ephemeral=True,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(NewsletterAutopilot(bot))
