"""
reminder_autopilot.py – Reminder-Cog für automatische Discord-DMs vor Eventbeginn

Sendet alle 60 Sekunden eine Erinnerung an Teilnehmer von Events,
die in ca. 5 Minuten beginnen. Unterstützt Mehrsprachigkeit via fur_lang.i18n.
"""

import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks
from fur_lang.i18n import t  # ✅ Übersetzungsfunktion

log = logging.getLogger(__name__)
REMINDER_INTERVAL_SECONDS = 60  # Prüfung alle 60 Sekunden


class ReminderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminder_loop.start()

    def cog_unload(self):
        self.reminder_loop.cancel()

    def get_db_connection(self):
        from init_db_core import get_db_path

        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        return conn

    def get_user_language(self, user_id: int) -> str:
        """
        Holt die bevorzugte Sprache eines Benutzers aus der DB.
        Fallback ist "de".
        """
        try:
            db = self.get_db_connection()
            row = db.execute(
                "SELECT lang FROM users WHERE discord_id = ?",
                (str(user_id),)
            ).fetchone()
            db.close()
            if row and row["lang"]:
                return row["lang"]
        except Exception as e:
            log.warning(f"⚠️ Sprache für User {user_id} nicht ermittelbar: {e}")
        return "de"

    @tasks.loop(seconds=REMINDER_INTERVAL_SECONDS)
    async def reminder_loop(self):
        await self.bot.wait_until_ready()
        now = datetime.utcnow()
        window_start = (now + timedelta(minutes=5)).isoformat(timespec="seconds")
        window_end = (now + timedelta(minutes=6)).isoformat(timespec="seconds")

        try:
            db = self.get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT e.id AS event_id, e.title, e.event_time, ep.user_id
                FROM event_participants ep
                JOIN events e ON e.id = ep.event_id
                LEFT JOIN reminders_sent rs ON rs.event_id = ep.event_id AND rs.user_id = ep.user_id
                WHERE rs.id IS NULL AND datetime(e.event_time) BETWEEN ? AND ?
                """,
                (window_start, window_end),
            )
            reminders = cursor.fetchall()

            for row in reminders:
                user_id = int(row["user_id"])
                lang = self.get_user_language(user_id)

                try:
                    user = await self.bot.fetch_user(user_id)
                    if user is None:
                        raise ValueError("Unbekannter Benutzer")

                    message = t("reminder_event_5min", title=row["title"], lang=lang)

                    await user.send(message)

                    cursor.execute(
                        """
                        INSERT INTO reminders_sent (event_id, user_id, sent_at)
                        VALUES (?, ?, ?)
                        """,
                        (row["event_id"], row["user_id"], now.isoformat(timespec="seconds")),
                    )
                    db.commit()
                    log.info(f"📤 DM-Erinnerung an {user} ({lang}) gesendet.")
                except Exception as e:
                    log.warning(f"❌ Konnte DM an {row['user_id']} nicht senden: {e}")

            db.close()

        except Exception as e:
            log.error(f"❌ Fehler im Reminder-Loop: {e}", exc_info=True)


async def setup(bot: commands.Bot):
    """Registriert das Reminder-Cog beim Bot."""
    await bot.add_cog(ReminderCog(bot))
