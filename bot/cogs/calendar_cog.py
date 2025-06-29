import logging
import secrets
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import discord
from discord import app_commands
from discord.ext import commands, tasks

from config import Config
from fur_lang.i18n import t
from mongo_service import get_collection
from services.calendar_service import CalendarService
from utils.oauth_utils import (
    build_authorization_url,
    generate_code_challenge,
    generate_code_verifier,
)
from utils.timezone import convert_datetime, get_user_timezone

log = logging.getLogger(__name__)


def should_send_daily(dt: datetime) -> bool:
    """Return True when a daily reminder should be sent."""
    return dt.hour == 8


def should_send_weekly(dt: datetime) -> bool:
    """Return True when a weekly reminder should be sent."""
    return dt.weekday() == 6 and dt.hour == 12


class CalendarCog(commands.Cog):
    """Slash commands and reminders for the event calendar."""

    calendar = app_commands.Group(name="calendar", description="Calendar commands")

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.service = CalendarService()
        self.daily_loop.start()
        self.weekly_loop.start()

    def cog_unload(self) -> None:  # pragma: no cover - lifecycle
        self.daily_loop.cancel()
        self.weekly_loop.cancel()

    def _get_user_timezone(self, user_id: int) -> ZoneInfo:
        user = get_collection("users").find_one({"discord_id": str(user_id)})
        return get_user_timezone(user)

    async def _send_events_dm(self, user: discord.User, events: list[dict], title: str) -> None:
        tz = self._get_user_timezone(user.id)
        embed = discord.Embed(title=title, colour=discord.Colour.blue())
        if not events:
            embed.description = t("calendar_no_events")
        for ev in events:
            when = ev.get("event_time")
            if when:
                when = convert_datetime(when, tz)
                dt_str = when.strftime("%d.%m %H:%M")
            else:
                dt_str = "TBA"
            embed.add_field(name=ev.get("title", "-"), value=dt_str, inline=False)
        try:
            await user.send(embed=embed)
            log.info("Sent events DM to %s with %d events", user.id, len(events))
        except discord.Forbidden:
            log.warning("DM blocked for %s", user.id)
        except Exception as exc:  # pragma: no cover - network failures
            log.warning("DM error for %s: %s", user.id, exc)

    @calendar.command(name="today", description="Show today's events")
    async def cmd_today(self, interaction: discord.Interaction) -> None:
        events = await self.service.get_events_today()
        await interaction.response.send_message(t("calendar_check_dm"), ephemeral=True)
        await self._send_events_dm(interaction.user, events, t("calendar_today_title"))

    @calendar.command(name="week", description="Show events this week")
    async def cmd_week(self, interaction: discord.Interaction) -> None:
        events = await self.service.get_events_week()
        await interaction.response.send_message(t("calendar_check_dm"), ephemeral=True)
        await self._send_events_dm(interaction.user, events, t("calendar_week_title"))

    @calendar.command(name="link", description="Link your Google Calendar")
    async def cmd_link(self, interaction: discord.Interaction) -> None:
        verifier = generate_code_verifier()
        challenge = generate_code_challenge(verifier)
        state = secrets.token_urlsafe(16)
        get_collection("oauth_states").update_one(
            {"discord_id": str(interaction.user.id)},
            {"$set": {"verifier": verifier, "state": state}},
            upsert=True,
        )
        url = build_authorization_url(
            Config.GOOGLE_CLIENT_ID,
            Config.GOOGLE_REDIRECT_URI,
            Config.GOOGLE_CALENDAR_SCOPES,
            state,
            challenge,
        )
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Authorize", url=url))
        await interaction.response.send_message(t("calendar_link_start"), view=view, ephemeral=True)

    @calendar.command(name="timezone", description="Set your timezone")
    async def cmd_timezone(self, interaction: discord.Interaction, name: str) -> None:
        tz = get_user_timezone({"timezone": name})
        get_collection("users").update_one(
            {"discord_id": str(interaction.user.id)},
            {"$set": {"timezone": tz.key}},
            upsert=True,
        )
        await interaction.response.send_message(
            t("calendar_timezone_set", zone=tz.key), ephemeral=True
        )

    async def _send_reminders(self, events: list[dict], title: str) -> None:
        guild = self.bot.get_guild(Config.DISCORD_GUILD_ID)
        if not guild:
            log.warning("Guild not found for calendar reminders")
            return
        for member in guild.members:
            if member.bot:
                continue
            await self._send_events_dm(member, events, title)

    @tasks.loop(hours=1)
    async def daily_loop(self) -> None:
        await self.bot.wait_until_ready()
        now = datetime.now(timezone.utc)
        if should_send_daily(now):
            events = await self.service.get_events_today()
            await self._send_reminders(events, t("calendar_today_title"))

    @tasks.loop(hours=1)
    async def weekly_loop(self) -> None:
        await self.bot.wait_until_ready()
        now = datetime.now(timezone.utc)
        if should_send_weekly(now):
            events = await self.service.get_events_week()
            await self._send_reminders(events, t("calendar_week_title"))


async def setup(bot: commands.Bot) -> None:
    """Set up the CalendarCog without duplicate command registration."""
    if bot.get_cog("CalendarCog") is not None:
        log.warning("CalendarCog already loaded – skipping")
        return

    await bot.add_cog(CalendarCog(bot))
