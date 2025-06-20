"""
database/__init__.py – Initialisiert die MongoDB-Verbindung für das FUR-System

Exportiert:
- `db`: Globale MongoDB-Datenbankinstanz
- `close_db()`: Platzhalter für Kompatibilität mit Flask-Teardown oder Tests
"""

from mongo_service import db  # noqa: F401


def close_db(e=None):
    """MongoDB verwendet Connection Pooling. Kein explizites Schließen nötig."""
    return None
