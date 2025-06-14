import os
import sqlite3

from config import Config


def get_db():
    """Return a SQLite connection with row factory enabled."""
    db_path = os.getenv("DATABASE_URL", Config.DATABASE_URL)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
