"""
web/__init__.py – Flask Application Factory

Erstellt die Flask-App, lädt alle Blueprints, konfiguriert Flask-Babel für Mehrsprachigkeit,
und bindet die zentrale Config-Klasse aus dem Projekt-Root ein.
"""

from flask import Flask
from flask_babel import Babel
from config import Config

def create_app():
    """
    Erstellt und konfiguriert die Flask-Anwendung (Application Factory Pattern).

    Returns:
        Flask: Die fertig konfigurierte Flask-App.
    """
    app = Flask(__name__)
    app.config.from_object(Config)  # <- Modern, kompatibel, keine Pfadprobleme

    # Flask-Babel für Mehrsprachigkeit (Standard: Deutsch)
    app.config.setdefault("BABEL_DEFAULT_LOCALE", "de")
    app.config.setdefault("BABEL_TRANSLATION_DIRECTORIES", "translations")
    babel = Babel(app)

    try:
        # Projekt-Blueprints importieren (Pfad ggf. anpassen!)
        from web.routes.public_routes import public_bp
        from web.routes.member_routes import member_bp
        from web.routes.admin_routes import admin_bp

        app.register_blueprint(public_bp)
        app.register_blueprint(member_bp, url_prefix="/members")
        app.register_blueprint(admin_bp, url_prefix="/admin")

        app.logger.info("✅ Alle Blueprints erfolgreich registriert.")

    except Exception as e:
        app.logger.error(f"Blueprint registration failed: {e}", exc_info=True)

    return app
