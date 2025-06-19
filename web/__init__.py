"""Flask application factory for the FUR system."""

import os
from pathlib import Path

from flask import Flask, request, session

from config import Config
from database import close_db
from flask_babel_next import Babel
from fur_lang.i18n import current_lang, get_supported_languages, t

# ---------------------------------------------------------------------------
# 🔹 Hilfsfunktion (Fallback für BG-Resolver)
# ---------------------------------------------------------------------------
try:
    from utils.bg_resolver import resolve_background_template
except ImportError:

    def resolve_background_template() -> str:
        return "/static/img/background.jpg"


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
    app.config.from_object(Config)

    # Mongo URI aus ENV (Railway / Docker)
    app.config["MONGODB_URI"] = os.getenv("MONGODB_URI")

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
    selector = getattr(babel, "localeselector", None)
    if selector is None:

        def selector(func):
            app.before_request(func)
            return func

    @selector
    def _select_locale() -> str | None:
        return session.get("lang") or request.accept_languages.best_match(
            app.config["BABEL_SUPPORTED_LOCALES"]
        )

    @app.before_request
    def set_language_from_request() -> None:
        lang = request.args.get("lang")
        if lang in app.config["BABEL_SUPPORTED_LOCALES"]:
            session["lang"] = lang

    # Globale Template-Variablen
    @app.context_processor
    def inject_globals():
        return {
            "t": t,
            "current_lang": current_lang,
            "resolve_background_template": resolve_background_template,
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
        from blueprints.reminder_api import reminder_api
        from dashboard.routes import dashboard

        app.register_blueprint(public)
        app.register_blueprint(member, url_prefix="/members")
        app.register_blueprint(admin, url_prefix="/admin")
        app.register_blueprint(leaderboard, url_prefix="/leaderboard")
        app.register_blueprint(reminder_api, url_prefix="/api/reminders")
        app.register_blueprint(dashboard)

        # API-Blueprints
        app.register_blueprint(api_events)
        app.register_blueprint(api_users)

        app.logger.info("✅ Alle Blueprints erfolgreich registriert.")
    except Exception:
        app.logger.exception("❌ Blueprint registration failed")

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

    return app
