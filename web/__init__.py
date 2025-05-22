"""
web/__init__.py – Flask Application Factory

Erstellt die Flask-App, lädt alle Blueprints, konfiguriert Flask-Babel für Mehrsprachigkeit
und sorgt für saubere Fehlerbehandlung beim Blueprint-Import.
"""

from flask import Flask
from flask_babel import Babel

def create_app() -> Flask:
    """
    Erstellt die zentrale Flask-Anwendung, konfiguriert i18n und registriert alle Blueprints.

    Returns:
        Flask: Die konfigurierte Flask-App.
    """
    app = Flask(__name__)
    app.config.from_pyfile("config.py")

    # Flask-Babel für Mehrsprachigkeit (Standard: Deutsch)
    app.config.setdefault("BABEL_DEFAULT_LOCALE", "de")
    app.config.setdefault("BABEL_TRANSLATION_DIRECTORIES", "translations")
    babel = Babel(app)

    try:
        # Projekt-Blueprints importieren (anpassen, falls Pfade anders!)
        from web.routes.public_routes import public_bp
        from web.routes.member_routes import member_bp
        from web.routes.admin_routes import admin_bp

        app.register_blueprint(public_bp)  # Öffentlich sichtbar
        app.register_blueprint(member_bp, url_prefix="/members")  # R3+, R4, Owner
        app.register_blueprint(admin_bp, url_prefix="/admin")     # R4+, Owner

        app.logger.info("✅ Alle Blueprints erfolgreich registriert.")

    except Exception as e:
        app.logger.error(f"Blueprint registration failed: {e}", exc_info=True)

    return app
