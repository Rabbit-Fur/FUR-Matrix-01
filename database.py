# database.py – Zentrale DB-Verwaltung für das FUR System

import sqlite3
from flask import g, current_app


def get_db():
    """Gibt eine SQLite-Datenbankverbindung aus dem Config-Wert zurück."""
    if 'db' not in g:
        db_path = current_app.config["DATABASE_URL"].replace("sqlite:///", "")
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row  # Zugriff auf Spalten per Name
    return g.db


def close_db(e=None):
    """Beendet die DB-Verbindung am Ende des Requests (falls geöffnet)."""
    db = g.pop('db', None)
    if db is not None:
        db.close()
