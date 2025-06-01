"""
web/__init__.py – Flask Application Factory

Erstellt die Flask-App, lädt alle Blueprints, konfiguriert JSON-basierte Mehrsprachigkeit
und bindet die zentrale Config-Klasse aus dem Projekt-Root ein.
"""

import os
from flask import Flask
from config import Config
from fur_lang.i18n import get_supported_languages

def create_app():
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_folder = os.path.join(base_dir, "templates")

    app = Flask(__name__, template_folder=template_folder)
    app.config.from_object(Config)

    # Lokale Sprachkonfiguration für FUR-LANG
    app.config["BABEL_DEFAULT_LOCALE"] = "de"
    app.config["BABEL_SUPPORTED_LOCALES"] = get_supported_languages()

    try:
        # Blueprint-Registrierung
        from web.routes.public_routes import public_bp
        from web.routes.member_routes import member_bp
        from web.routes.admin_routes import admin_bp

        app.register_blueprint(public_bp)
        app.register_blueprint(member_bp, url_prefix="/members")
        app.register_blueprint(admin_bp, url_prefix="/admin")

        app.logger.info("✅ Alle Blueprints erfolgreich registriert.")

    except Exception as e:
        app.logger.error(f"Blueprint registration failed: {e}", exc_info=True)

    # Debug-Ausgabe
    app.logger.info(f"TEMPLATE_ROOT = {app.template_folder}")
    if not os.path.exists(os.path.join(app.template_folder, "public/landing.html")):
        app.logger.error("❌ landing.html nicht gefunden! Kontrolliere den Pfad.")

    return app
