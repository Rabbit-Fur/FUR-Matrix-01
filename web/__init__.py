"""
web/__init__.py – Flask Application Factory für FUR SYSTEM

Erstellt die Flask-App, lädt alle Blueprints, konfiguriert JSON-basierte Mehrsprachigkeit
und bindet die zentrale Config-Klasse aus dem Projekt-Root ein.
"""

import os

from flask import Flask
from flask_babel import Babel

from config import Config
from fur_lang.i18n import get_supported_languages


def create_app():
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_folder = os.path.join(base_dir, "templates")
    static_folder = os.path.join(base_dir, "static")

    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    app.config.from_object(Config)

    # Flask-Babel für Mehrsprachigkeit
    app.config.setdefault("BABEL_DEFAULT_LOCALE", "de")
    app.config.setdefault("BABEL_SUPPORTED_LOCALES", get_supported_languages())
    app.config.setdefault(
        "BABEL_TRANSLATION_DIRECTORIES", os.path.join(base_dir, "translations")
    )
    babel = Babel(app)

    try:
        from dashboard.routes import dashboard  # NEU!
        from web.routes.admin_routes import admin_bp
        from web.routes.member_routes import member_bp
        from web.routes.public_routes import public_bp
        from web.routes.reminder_api import reminder_api

        app.register_blueprint(public_bp)
        app.register_blueprint(member_bp, url_prefix="/members")
        app.register_blueprint(admin_bp)
        app.register_blueprint(reminder_api)
        app.register_blueprint(dashboard)

        app.logger.info("✅ Alle Blueprints erfolgreich registriert.")

    except Exception as e:
        app.logger.error(f"Blueprint registration failed: {e}", exc_info=True)

    # Debug-Ausgabe
    app.logger.info(f"TEMPLATE_ROOT = {app.template_folder}")
    if not os.path.exists(os.path.join(app.template_folder, "public/landing.html")):
        app.logger.error("❌ landing.html nicht gefunden! Kontrolliere den Pfad.")

    return app
