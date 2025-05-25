"""
reminder_cog.py – Discord-Cog für individuelle Event-Reminder per DM

Dieses Cog prüft regelmäßig (alle 5 Minuten) bevorstehende Events
und verschickt personalisierte DMs an alle Teilnehmer, falls sie noch keine Erinnerung erhalten haben.
Die Erinnerungen werden protokolliert, um Mehrfachbenachrichtigungen zu vermeiden.
"""

import logging
import sqlite3
from datetime import datetime, timedelta

import discord
from bot.bot_main import get_bot_db_connection as get_db
from discord.ext import commands, tasks

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
                    """
                    SELECT user_id
                    FROM participants
                    WHERE event_id = ?
                    """,
                    (event["id"],),
                ).fetchall()

                for p in participants:
                    already_sent = db.execute(
                        """
                        SELECT 1 FROM reminders_sent
                        WHERE event_id = ? AND user_id = ?
                        """,
                        (event["id"], p["user_id"]),
                    ).fetchone()

                    if already_sent:
                        continue

                    user = self.bot.get_user(int(p["user_id"]))
                    if not user:
                        try:
                            user = await self.bot.fetch_user(int(p["user_id"]))
                        except discord.NotFound:
                            log.warning(f"User ID {p['user_id']} not found.")
                            continue

                    try:
                        await user.send(
                            f"⏰ **Reminder:** Dein Event **'{event['title']}'** startet in weniger als 15 Minuten!"
                        )
                        db.execute(
                            """
                            INSERT INTO reminders_sent (event_id, user_id, sent_at)
                            VALUES (?, ?, ?)
                            """,
                            (event["id"], p["user_id"], datetime.utcnow().isoformat()),
                        )
                        db.commit()
                        log.info(f"✅ Reminder sent to {p['user_id']} for event {event['id']}")
                    except discord.Forbidden:
                        log.warning(f"Cannot DM user {p['user_id']}: DMs disabled.")
                    except Exception as e:
                        log.error(f"Failed to send DM to {p['user_id']}: {e}")

        except sqlite3.Error as e:
            log.error(f"Database error during reminder check: {e}", exc_info=True)
        except Exception as e:
            log.error(f"Unexpected error during reminder check: {e}", exc_info=True)

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
