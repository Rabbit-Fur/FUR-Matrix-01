"""
tests/conftest.py – Zentrale Pytest-Konfiguration & Fixtures für das FUR-System

Stellt Fixtures für Flask-App, Test-Client, und Datenbank-Setup bereit.
Erleichtert Unit- und Integrationstests aller Komponenten (Web, Bot, DB).
"""

import os

# Defaultwerte für benötigte Umgebungsvariablen setzen, damit die Konfiguration
# auch in der Testumgebung ohne .env funktioniert.
os.environ.setdefault("DISCORD_TOKEN", "dummy")
os.environ.setdefault("DISCORD_GUILD_ID", "1")
os.environ.setdefault("REMINDER_CHANNEL_ID", "1")
os.environ.setdefault("SECRET_KEY", "test")
os.environ.setdefault("DISCORD_CLIENT_ID", "1")
os.environ.setdefault("DISCORD_CLIENT_SECRET", "dummy")
os.environ.setdefault("DISCORD_REDIRECT_URI", "http://localhost:8080/callback")
os.environ.setdefault("SESSION_LIFETIME_MINUTES", "60")
os.environ.setdefault("R3_ROLE_IDS", "1")
os.environ.setdefault("R4_ROLE_IDS", "1")
os.environ.setdefault("ADMIN_ROLE_IDS", "1")
os.environ.setdefault("BASE_URL", "http://localhost:8080")

import pytest

from init_db_core import get_db_connection, init_db
from web import create_app


@pytest.fixture(scope="session")
def app():
    """
    Gibt eine konfigurierbare Flask-App für Tests zurück.
    """
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SERVER_NAME": "localhost:8080",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )
    with app.app_context():
        init_db()
        yield app


@pytest.fixture(scope="session")
def client(app):
    """
    Gibt einen Flask-Test-Client zurück.
    """
    return app.test_client()


@pytest.fixture(scope="session")
def db_conn():
    """
    Liefert eine Datenbankverbindung für Tests (z.B. für direkte DB-Checks).
    """
    conn = get_db_connection()
    yield conn
    conn.close()
