"""
init_db_core.py – Initialisiert die SQLite-Datenbank für das FUR-System

Legt beim ersten Start alle notwendigen Tabellen an (User, Events, Teilnehmer, Reminder, Hall of Fame).
"""

import logging
import os
import sqlite3

DB_PATH = os.getenv("DATABASE_URL") or os.path.join(
    os.path.dirname(__file__), "data", "admin_users.db"
)
log = logging.getLogger(__name__)


def get_db_connection() -> sqlite3.Connection:
    """
    Stellt eine Verbindung zur SQLite-Datenbank her.

    Returns:
        sqlite3.Connection: Aktive DB-Verbindung.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initialisiert die Datenbank: Legt Tabellen an, falls sie fehlen.
    Wird beim App-Start ausgeführt.
    """
    schema = [
        # Admin/User-Tabelle (Rollen)
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            discord_id TEXT,
            created_at TEXT NOT NULL
        );
        """,
        # Events
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_time TEXT NOT NULL,
            created_by INTEGER NOT NULL,
            description TEXT,
            FOREIGN KEY (created_by) REFERENCES users(id)
        );
        """,
        # Teilnehmer
        """
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """,
        # Reminder-Status
        """
        CREATE TABLE IF NOT EXISTS reminders_sent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            sent_at TEXT NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """,
        # Custom Reminders
        """
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            send_time TEXT,
            created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users(id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS reminder_participants (
            reminder_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY (reminder_id, user_id),
            FOREIGN KEY (reminder_id) REFERENCES reminders(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS reminder_optout (
            user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE
        );
        """,
        # Hall of Fame (Champions)
        """
        CREATE TABLE IF NOT EXISTS hall_of_fame (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            honor_title TEXT,
            month TEXT,
            poster_url TEXT,
            created_at TEXT
        );
        """,
    ]

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        for stmt in schema:
            cursor.executescript(stmt)
        conn.commit()
        conn.close()
        log.info("✅ Datenbank initialisiert/aktualisiert (%s)", DB_PATH)
    except Exception as e:
        log.error("❌ Fehler bei DB-Initialisierung: %s", e, exc_info=True)
