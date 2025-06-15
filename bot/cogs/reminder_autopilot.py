"""
reminder_autopilot.py – Reminder-Cog für automatische Discord-DMs vor Eventbeginn

Wird alle 60 Sekunden ausgeführt und sendet Erinnerungen an Teilnehmer
von Events, die in 5 Minuten starten. Erinnerungen werden nur einmal versendet.
"""

import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

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
                try:
                    user = await self.bot.fetch_user(int(row["user_id"]))
                    if user is None:
                        raise ValueError("Unbekannter Benutzer")
                    await user.send(
                        f"⏰ Erinnerung: Das Event **{row['title']}** beginnt in ca. 5 Minuten!"
                    )
                    cursor.execute(
                        """
                        INSERT INTO reminders_sent (event_id, user_id, sent_at)
                        VALUES (?, ?, ?)
                        """,
                        (row["event_id"], row["user_id"], now.isoformat(timespec="seconds")),
                    )
                    db.commit()
                    log.info(f"📤 DM-Erinnerung an {user} gesendet.")
                except Exception as e:
                    log.warning(f"❌ Konnte DM an {row['user_id']} nicht senden: {e}")

            db.close()

        except Exception as e:
            log.error(f"❌ Fehler im Reminder-Loop: {e}", exc_info=True)


async def setup(bot: commands.Bot):
    """Registriert das Cog im Bot."""
    await bot.add_cog(ReminderCog(bot))
