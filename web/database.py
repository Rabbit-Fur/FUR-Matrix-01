import sqlite3

from init_db_core import get_db_path


def get_db():
    """Return a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(get_db_path())
    db_path = os.getenv("DATABASE_URL", Config.DATABASE_URL)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
