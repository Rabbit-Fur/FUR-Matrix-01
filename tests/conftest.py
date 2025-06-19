"""Pytest configuration for FUR system using MongoDB."""

import os

import pytest

# environment for Flask app
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

from web import create_app  # noqa: E402


@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config.update({"TESTING": True, "WTF_CSRF_ENABLED": False, "SERVER_NAME": "localhost:8080"})
    with app.app_context():
        yield app


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()
