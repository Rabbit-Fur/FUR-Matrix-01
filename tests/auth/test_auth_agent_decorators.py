from flask import Blueprint, Flask
import sys
from pathlib import Path
import os

sys.path.append(str(Path(__file__).resolve().parents[2]))
os.environ["MONGODB_URI"] = "mongodb://localhost:27017/testdb"
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
os.environ.setdefault("GOOGLE_REDIRECT_URI", "http://localhost:8080/oauth2callback")
os.environ.setdefault("GOOGLE_CREDENTIALS_FILE", "/tmp/google.json")
os.environ.setdefault("GOOGLE_CALENDAR_SCOPES", "https://www.googleapis.com/auth/calendar.readonly")
os.environ.setdefault("GOOGLE_CLIENT_ID", "gid")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "gsecret")
os.environ.setdefault("BABEL_DEFAULT_LOCALE", "en")

from agents.auth_agent import AuthAgent  # noqa: E402
from web.auth.decorators import (  # noqa: E402
    admin_required,
    login_required,
    r3_required,
    r4_required,
)


def _create_app():
    app = Flask(__name__)
    app.secret_key = "test"

    public = Blueprint("public", __name__)

    @public.route("/login")
    def login():
        return "login"

    app.register_blueprint(public)

    @app.route("/protected")
    @login_required
    def protected():
        return "ok"

    @app.route("/r3")
    @r3_required
    def r3_route():
        return "r3"

    @app.route("/r4")
    @r4_required
    def r4_route():
        return "r4"

    @app.route("/admin")
    @admin_required
    def admin_route():
        return "admin"

    return app


def test_auth_agent_role_helpers():
    auth = AuthAgent({}, None)
    assert not auth.is_r3()
    assert not auth.is_r4()
    assert not auth.is_admin()

    auth = AuthAgent({"user": {"role_level": "R3"}}, None)
    assert auth.is_r3()
    assert not auth.is_r4()
    assert not auth.is_admin()

    auth = AuthAgent({"user": {"role_level": "R4"}}, None)
    assert auth.is_r3()
    assert auth.is_r4()
    assert not auth.is_admin()

    auth = AuthAgent({"user": {"role_level": "ADMIN"}}, None)
    assert auth.is_r3()
    assert auth.is_r4()
    assert auth.is_admin()


def test_role_decorators_enforce_access():
    app = _create_app()
    client = app.test_client()

    # login_required
    resp = client.get("/protected")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")

    with client.session_transaction() as sess:
        sess["user"] = {"role_level": "R3"}

    assert client.get("/protected").status_code == 200

    # r3 route
    resp = client.get("/r3")
    assert resp.status_code == 200

    # r4 route requires upgrade
    resp = client.get("/r4")
    assert resp.status_code == 302

    with client.session_transaction() as sess:
        sess["user"] = {"role_level": "R4"}

    assert client.get("/r4").status_code == 200
    assert client.get("/admin").status_code == 302

    with client.session_transaction() as sess:
        sess["user"] = {"role_level": "ADMIN"}

    assert client.get("/admin").status_code == 200
