from discord.ext import commands

from web.database import get_db


class ReminderOptOut(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def reminder(self, ctx: commands.Context, action: str | None = None) -> None:
        if action and action.lower() == "stop":
            db = get_db()
            db.execute(
                "INSERT OR IGNORE INTO reminder_optout (user_id) "
                "SELECT id FROM users WHERE discord_id = ?",
                (ctx.author.id,),
            )
            db.commit()
            db.close()
            await ctx.send("✅ You will no longer receive reminder DMs.")


async def setup(bot: commands.Bot) -> None:
    """Register the cog using discord.py's async setup convention."""
    await bot.add_cog(ReminderOptOut(bot))
