"""
reminder_cog.py – Discord-Cog für individuelle Event-Reminder per DM

Dieses Cog prüft regelmäßig (alle 5 Minuten) bevorstehende Events
und verschickt personalisierte DMs an alle Teilnehmer, falls sie noch keine Erinnerung erhalten haben.
Die Erinnerungen werden protokolliert, um Mehrfachbenachrichtigungen zu vermeiden.
"""

import logging
from datetime import datetime, timedelta
import discord
from discord.ext import commands, tasks

from web.database import get_db
from fur_lang.i18n import t

log = logging.getLogger(__name__)


class ReminderCog(commands.Cog):
    """
    Cog: Event-Reminders per Discord-DM.

    - Prüft regelmäßig bevorstehende Events im DB-Fenster (nächste 10–15 Minuten).
    - Sendet DMs nur, wenn sie noch nicht für dieses Event/User verschickt wurden.
    - Loggt alle Aktionen und Fehler.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_reminders.start()

    def cog_unload(self) -> None:
        """Stoppt den Reminder-Loop beim Entladen des Cogs."""
        self.check_reminders.cancel()

    def get_user_language(self, user_id: int) -> str:
        """
        Holt die bevorzugte Sprache eines Benutzers aus der DB.
        Fallback: 'de'.
        """
        try:
            db = get_db()
            row = db.execute(
                "SELECT lang FROM users WHERE discord_id = ?", (str(user_id),)
            ).fetchone()
            if row and row["lang"]:
                return row["lang"]
        except Exception as e:
            log.warning(f"⚠️ Sprache für User {user_id} nicht ermittelbar: {e}")
        return "de"

    @tasks.loop(minutes=5.0)
    async def check_reminders(self) -> None:
        """
        Task: Durchsucht die Events in der Datenbank und verschickt Erinnerungs-DMs
        an alle Teilnehmer, die in Kürze (10–15 min) starten.
        """
        now = datetime.utcnow()
        window_start = now + timedelta(minutes=10)
        window_end = now + timedelta(minutes=15)

        try:
            db = get_db()
            events = db.execute(
                """
                SELECT id, title, event_time
                FROM events
                WHERE datetime(event_time) BETWEEN ? AND ?
                """,
                (window_start.isoformat(), window_end.isoformat()),
            ).fetchall()

            for event in events:
                participants = db.execute(
                    "SELECT user_id FROM participants WHERE event_id = ?",
                    (event["id"],),
                ).fetchall()

                for p in participants:
                    user_id = int(p["user_id"])

                    already_sent = db.execute(
                        "SELECT 1 FROM reminders_sent WHERE event_id = ? AND user_id = ?",
                        (event["id"], user_id),
                    ).fetchone()

                    if already_sent:
                        continue

                    lang = self.get_user_language(user_id)

                    try:
                        user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
                        if not user:
                            log.warning(f"User ID {user_id} not found.")
                            continue

                        msg = t("reminder_event_15min", title=event["title"], lang=lang)
                        await user.send(msg)

                        db.execute(
                            "INSERT INTO reminders_sent (event_id, user_id, sent_at) VALUES (?, ?, ?)",
                            (event["id"], user_id, now.isoformat(timespec="seconds")),
                        )
                        db.commit()
                        log.info(f"📤 15-Minuten-Reminder an {user_id} gesendet.")
                    except discord.Forbidden:
                        log.warning(f"🚫 DMs deaktiviert bei User {user_id}")
                    except Exception as e:
                        log.error(f"❌ Fehler beim Senden an {user_id}: {e}")

        except Exception as e:
            log.error(f"❌ Fehler beim Reminder-Check: {e}", exc_info=True)

    @check_reminders.before_loop
    async def before_check_reminders(self) -> None:
        """Wartet bis der Bot vollständig bereit ist, bevor Reminder-Loop startet."""
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot) -> None:
    """
    Registriert das ReminderCog beim Bot.

    Args:
        bot (commands.Bot): Discord-Bot-Instanz.
    """
    await bot.add_cog(ReminderCog(bot))
