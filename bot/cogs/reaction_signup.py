"""reaction_signup.py – Save 🔥 reactions as event participation."""

from __future__ import annotations

import logging
import re
from datetime import datetime

import discord
from bson import ObjectId
from discord.ext import commands

from mongo_service import get_collection

log = logging.getLogger(__name__)

EVENT_ID_RE = re.compile(r"\[ID:(?P<id>[a-fA-F0-9]{24})\]")


class ReactionSignup(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _extract_event_id(self, message: discord.Message) -> ObjectId | None:
        match = EVENT_ID_RE.search(message.content)
        if not match:
            return None
        try:
            return ObjectId(match.group("id"))
        except Exception:
            return None

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        if str(payload.emoji) != "🔥":
            return
        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            return
        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception as exc:  # noqa: BLE001
            log.warning("Could not fetch message: %s", exc)
            return

        event_id = await self._extract_event_id(message)
        if not event_id:
            return

        if not get_collection("events").find_one({"_id": event_id}):
            log.warning("Invalid event id %s", event_id)
            return

        collection = get_collection("event_participants")
        collection.update_one(
            {"event_id": event_id, "user_id": str(payload.user_id)},
            {
                "$setOnInsert": {
                    "event_id": event_id,
                    "user_id": str(payload.user_id),
                    "joined_at": datetime.utcnow(),
                }
            },
            upsert=True,
        )
        log.info("User %s joined event %s via reaction", payload.user_id, event_id)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ReactionSignup(bot))
