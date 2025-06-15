"""
web/__init__.py – Flask Application Factory für FUR SYSTEM

Erstellt die Flask-App, lädt alle Blueprints, konfiguriert JSON-basierte Mehrsprachigkeit
und bindet die zentrale Config-Klasse aus dem Projekt-Root ein.
"""

import os

from flask import Flask, request, session
from flask_babel_next import Babel

from config import Config
from database import close_db
from fur_lang.i18n import current_lang, get_supported_languages, t

try:
    from utils.bg_resolver import resolve_background_template
except ImportError:
    resolve_background_template = lambda: "/static/img/background.jpg"


def create_app():
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_folder = os.path.join(base_dir, "templates")
    static_folder = os.path.join(base_dir, "static")

    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    app.config.from_object(Config)

    # 🌍 Flask-Babel (i18n)
    app.config.setdefault("BABEL_DEFAULT_LOCALE", "de")
    app.config.setdefault("BABEL_SUPPORTED_LOCALES", get_supported_languages())
    app.config.setdefault(
        "BABEL_TRANSLATION_DIRECTORIES", os.path.join(base_dir, "translations")
    )

    babel = Babel()
    babel.init_app(app)

    # ✅ Richtiger Aufruf: am Babel-Objekt, nicht Flask
    def get_locale():
        return session.get("lang") or request.accept_languages.best_match(
            app.config["BABEL_SUPPORTED_LOCALES"]
        )

    babel.locale_selector_func(get_locale)  # ✅ korrekt!

    # 🌐 Sprache manuell via ?lang=
    @app.before_request
    def set_language_from_request():
        lang = request.args.get("lang")
        if lang in app.config["BABEL_SUPPORTED_LOCALES"]:
            session["lang"] = lang

    # 🌐 Globale Jinja2-Funktionen
    @app.context_processor
    def inject_globals():
        return {
            "t": t,
            "current_lang": current_lang,
            "resolve_background_template": resolve_background_template,
        }

    # 🧩 Blueprints laden
    try:
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

        app.logger.info("✅ Alle Blueprints erfolgreich registriert.")
    except Exception:
        app.logger.error("❌ Blueprint registration failed:", exc_info=True)

    # 📦 DB-Teardown bei AppContext-Ende
    app.teardown_appcontext(close_db)

    # 📂 Template-Prüfung
    app.logger.info(f"TEMPLATE_ROOT = {app.template_folder}")
    if not os.path.exists(os.path.join(app.template_folder, "public/landing.html")):
        app.logger.error("❌ landing.html nicht gefunden! Kontrolliere den Pfad.")

    return app
