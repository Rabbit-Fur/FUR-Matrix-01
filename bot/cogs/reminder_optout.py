"""Opt-out cog using MongoDB."""

import logging

from discord.ext import commands

from fur_lang.i18n import t
from mongo_service import get_collection

log = logging.getLogger(__name__)


class ReminderOptOut(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def reminder(self, ctx: commands.Context, action: str | None = None) -> None:
        lang = "de"
        discord_id = str(ctx.author.id)

        if action and action.lower() == "stop":
            try:
                collection = get_collection("reminder_optout")
                collection.update_one(
                    {"discord_id": discord_id}, {"$set": {"discord_id": discord_id}}, upsert=True
                )
                log.info(f"🚫 User {discord_id} hat Reminder deaktiviert.")
                await ctx.send(t("reminder_optout_success", lang=lang))
            except Exception as e:
                log.error(f"❌ Fehler beim Reminder-Opt-Out für {discord_id}: {e}")
                await ctx.send(t("reminder_optout_error", lang=lang))
        else:
            await ctx.send(t("reminder_optout_usage", lang=lang))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ReminderOptOut(bot))
