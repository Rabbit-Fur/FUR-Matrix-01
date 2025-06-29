"""Pytest configuration for FUR system using MongoDB."""

import asyncio
import os

import pytest

# environment for Flask app
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017/testdb")
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
os.environ.setdefault(
    "GOOGLE_REDIRECT_URI",
    "http://localhost:8080/oauth2callback",
)
os.environ.setdefault("GOOGLE_CREDENTIALS_FILE", "/tmp/google.json")
os.environ.setdefault(
    "GOOGLE_CALENDAR_SCOPES",
    "https://www.googleapis.com/auth/calendar.readonly",
)
os.environ.setdefault("GOOGLE_CLIENT_ID", "gid")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "gsecret")

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())


@pytest.fixture(autouse=True)
def ensure_loop():
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    yield


import web  # noqa: E402
from flask_babel_next import Babel as _BaseBabel  # noqa: E402

web.Babel = _BaseBabel

import mongomock  # noqa: E402

import mongo_service  # noqa: E402
from web import create_app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _mock_db():
    client = mongomock.MongoClient()
    mongo_service.client = client
    mongo_service.db = client["testdb"]
    yield


@pytest.fixture(scope="session")
def app():
    app = create_app()

    from flask import Blueprint

    public = Blueprint("public", __name__)

    @public.route("/set_language")
    def set_language():
        return "ok"

    @public.route("/")
    def landing():
        return "home"

    @public.route("/dashboard")
    def public_dashboard():
        return "dash"

    @public.route("/events")
    def events():
        return "events"

    @public.route("/leaderboard")
    def leaderboard():
        return "lb"

    @public.route("/hall_of_fame")
    def hall_of_fame():
        return "hof"

    @public.route("/lore")
    def lore():
        return "lore"

    app.register_blueprint(public, name="public_test")

    admin_bp = Blueprint("admin", __name__)

    @admin_bp.route("/dashboard")
    def admin_dashboard():
        return "admindash"

    app.register_blueprint(admin_bp, url_prefix="/admin", name="admin_test")

    member_bp = Blueprint("member", __name__)

    @member_bp.route("/dashboard")
    def member_dashboard():
        return "memberdash"

    app.register_blueprint(member_bp, url_prefix="/members", name="member_test")

    app.config.update({"TESTING": True, "WTF_CSRF_ENABLED": False, "SERVER_NAME": "localhost:8080"})
    with app.app_context():
        yield app


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()
