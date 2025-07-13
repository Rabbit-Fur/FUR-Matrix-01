import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

from bot.dm_scheduler import get_dm_users
from mongo_service import get_collection

log = logging.getLogger(__name__)

INTRO_JSON = Path("AI_Intro-Image.json")
INTRO_IMAGE = Path("static/img/SORRY.png")


class IntroCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        asyncio.create_task(self._maybe_send_intro())
        async def _hook(self):
        await self.bot.wait_until_ready()
        await self._maybe_send_intro()

    async def cog_load(self):
        self.bot.loop.create_task(self._hook())

    @staticmethod
    def _load_embed() -> discord.Embed | None:
        if not INTRO_JSON.is_file():
            log.warning("intro json missing")
            return None
        try:
            data = json.loads(INTRO_JSON.read_text())
            embed_data = data.get("embeds", [{}])[0]
            return discord.Embed.from_dict(embed_data)
        except Exception as exc:  # noqa: BLE001
            log.error("failed to load intro json: %s", exc)
            return None

    async def _send_intro(self) -> None:
        embed = self._load_embed()
        if not embed or not INTRO_IMAGE.is_file():
            return
        file_path = INTRO_IMAGE
        for uid in get_dm_users():
            try:
                user = await self.bot.fetch_user(uid)
                await user.send(embed=embed, file=discord.File(file_path))
            except Exception as exc:  # noqa: BLE001
                log.error("intro DM to %s failed: %s", uid, exc)

    async def _maybe_send_intro(self) -> None:
        await self.bot.wait_until_ready()
        flags = get_collection("flags")
        if flags.find_one({"_id": "ai_intro_sent", "value": True}):
            return
        await self._send_intro()
        flags.update_one(
            {"_id": "ai_intro_sent"},
            {"$set": {"value": True, "sent_at": datetime.utcnow()}},
            upsert=True,
        )

    @app_commands.command(name="ai_sorry", description="Send intro message again")
    async def ai_sorry(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        await self._send_intro()
        get_collection("flags").update_one(
            {"_id": "ai_intro_sent"},
            {"$set": {"value": True, "sent_at": datetime.utcnow()}},
            upsert=True,
        )
        await interaction.followup.send("Intro message sent", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(IntroCog(bot))
