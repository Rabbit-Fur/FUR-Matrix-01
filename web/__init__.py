"""Flask application factory for the FUR system."""

import importlib
import os
from pathlib import Path

from flask import Blueprint, Flask, request, session
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from database import close_db
from flask_babel_next import Babel
from fur_lang.i18n import (
    current_lang,
    get_language_native_name,
    get_supported_languages,
    is_rtl,
    t,
)
from web.auth_routes import auth_bp
from web.champion_routes import champion_blueprint
from web.poster_routes import poster_blueprint
from web.reminder_routes import reminder_blueprint
from web.socketio_events import init_socketio
from blueprints.monitoring import monitoring

# ---------------------------------------------------------------------------
# 🔹 Hilfsfunktion (Fallback für BG-Resolver)
# ---------------------------------------------------------------------------
try:
    from utils.bg_resolver import resolve_background_template
except ImportError:

    def resolve_background_template() -> str:
        return "/static/img/background.jpg"


def auto_register_blueprints(app: Flask) -> None:
    """Automatically register all *_routes.py blueprints in this package."""
    routes_dir = Path(__file__).parent
    for route_file in routes_dir.glob("*_routes.py"):
        module_name = f"web.{route_file.stem}"
        module = importlib.import_module(module_name)
        for attr in dir(module):
            blueprint = getattr(module, attr)
            if isinstance(blueprint, Blueprint):
                if blueprint.name not in app.blueprints:
                    app.register_blueprint(blueprint)


# ---------------------------------------------------------------------------
# 🔹 Factory
# ---------------------------------------------------------------------------
def create_app() -> Flask:
    """Create and configure a Flask application instance."""
    base_dir = Path(__file__).resolve().parent.parent
    template_folder = base_dir / "templates"
    static_folder = base_dir / "static"

    app = Flask(
        __name__,
        template_folder=template_folder,
        static_folder=static_folder,
    )
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    # Ensure a secret key is set for session handling
    app.secret_key = os.environ.get("FLASK_SECRET", "fallback-dev-key")
    app.config.from_object(Config)

    # ---------------------------------------------------------------------
    # 🧠 1) Vorab-Blueprints (Memory-Viewer)
    # ---------------------------------------------------------------------
    from web.admin.memory_routes import admin_memory  # <- korrekter Import

    app.register_blueprint(admin_memory, url_prefix="/admin/memory")

    # ---------------------------------------------------------------------
    # 🌍 2) Babel-Konfiguration
    # ---------------------------------------------------------------------
    app.config.setdefault("BABEL_DEFAULT_LOCALE", "de")
    app.config.setdefault("BABEL_SUPPORTED_LOCALES", get_supported_languages())
    app.config.setdefault(
        "BABEL_TRANSLATION_DIRECTORIES",
        str(base_dir / "translations"),
    )

    babel = Babel()

    def get_locale() -> str:  # pragma: no cover - simple accessor
        return (
            session.get("lang")
            or request.accept_languages.best_match(app.config.get("BABEL_SUPPORTED_LOCALES", []))
            or app.config.get("BABEL_DEFAULT_LOCALE", "en")
        )

    babel.init_app(app, locale_selector=get_locale)

    @app.before_request
    def set_language_from_request() -> None:
        lang = request.args.get("lang")
        if lang in app.config["BABEL_SUPPORTED_LOCALES"]:
            session["lang"] = lang

    @app.context_processor
    def inject_globals():
        return {
            "t": t,
            "current_lang": current_lang,
            "resolve_background_template": resolve_background_template,
            "language_native_name": get_language_native_name,
            "is_rtl": is_rtl,
        }

    # ---------------------------------------------------------------------
    # 📦 3) Weitere Blueprints dynamisch laden
    # ---------------------------------------------------------------------
    try:
        from blueprints import api_events, api_users
        from blueprints.admin import admin
        from blueprints.leaderboard import leaderboard
        from blueprints.member import member
        from blueprints.public import public
        from blueprints.resources import resources as resources_bp
        from dashboard.routes import dashboard

        try:
            from blueprints.reminder_api import reminder_api
        except Exception:
            reminder_api = None

        if not app.config.get("TESTING"):
            app.register_blueprint(public)
        app.register_blueprint(member, url_prefix="/members")
        app.register_blueprint(admin, url_prefix="/admin")
        app.register_blueprint(leaderboard, url_prefix="/leaderboard")
        app.register_blueprint(resources_bp)
        if reminder_api:
            app.register_blueprint(reminder_api, url_prefix="/api/reminders")
        app.register_blueprint(dashboard)
        from services.google.auth import google_auth as google_auth_bp
        from web.routes.google_oauth_web import oauth_bp as google_oauth_web_bp

        app.register_blueprint(google_auth_bp)
        app.register_blueprint(google_oauth_web_bp)

        # API-Blueprints
        app.register_blueprint(api_events)
        app.register_blueprint(api_users)
        app.register_blueprint(monitoring)

        app.logger.info("✅ Alle Blueprints erfolgreich registriert.")
    except Exception:
        app.logger.exception("❌ Blueprint registration failed")

    app.register_blueprint(auth_bp)
    app.register_blueprint(champion_blueprint)
    app.register_blueprint(reminder_blueprint)
    app.register_blueprint(poster_blueprint)

    auto_register_blueprints(app)

    # ---------------------------------------------------------------------
    # 🧹 4) DB-Teardown
    # ---------------------------------------------------------------------
    app.teardown_appcontext(close_db)

    # ---------------------------------------------------------------------
    # 🔍 5) Template-Existenz prüfen (optional)
    # ---------------------------------------------------------------------
    landing_path = template_folder / "public" / "landing.html"
    if not landing_path.exists():
        app.logger.error(
            "❌ landing.html nicht gefunden! Kontrolliere den Pfad (%s).", landing_path
        )
    init_socketio(app)
    return app
