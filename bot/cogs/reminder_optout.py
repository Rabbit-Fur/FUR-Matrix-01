"""
reminder_optout.py – Cog für das Opt-Out-System von Event-Remindern

Erlaubt es Usern, sich mit dem Befehl `!reminder stop` von DMs abzumelden.
Die Einstellungen werden in der Tabelle `reminder_optout` gespeichert.
"""

import logging
from discord.ext import commands
from web.database import get_db
from fur_lang.i18n import t

log = logging.getLogger(__name__)


class ReminderOptOut(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def reminder(self, ctx: commands.Context, action: str | None = None) -> None:
        """
        Erlaubt einem Benutzer, Erinnerungs-DMs abzuschalten.
        Syntax: !reminder stop
        """
        lang = "de"  # Standard – später aus DB laden
        discord_id = str(ctx.author.id)

        if action and action.lower() == "stop":
            try:
                db = get_db()
                db.execute(
                    """
                    INSERT OR IGNORE INTO reminder_optout (user_id)
                    SELECT id FROM users WHERE discord_id = ?
                    """,
                    (discord_id,),
                )
                db.commit()
                db.close()
                log.info(f"🚫 User {discord_id} hat Reminder deaktiviert.")

                await ctx.send(t("reminder_optout_success", lang=lang))
            except Exception as e:
                log.error(f"❌ Fehler beim Reminder-Opt-Out für {discord_id}: {e}")
                await ctx.send(t("reminder_optout_error", lang=lang))
        else:
            await ctx.send(t("reminder_optout_usage", lang=lang))


async def setup(bot: commands.Bot) -> None:
    """Registriert das Opt-Out-Cog beim Bot."""
    await bot.add_cog(ReminderOptOut(bot))
