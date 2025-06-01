"""
web.app – Alternativer Flask-Einstiegspunkt für das FUR-System

Erstellt die Flask-App, lädt die zentrale Config, registriert alle Blueprints und ist bereit für Gunicorn/WSGI.
"""

from flask import Flask
from config import Config

def create_app() -> Flask:
    """
    Flask-Application-Factory (Best Practice).

    Returns:
        Flask: Die konfigurierte Flask-Anwendung.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Blueprint-Registrierungen
    try:
        from blueprints.public_routes import public_bp
        from blueprints.admin_routes import admin_bp
        from blueprints.member_routes import member_bp

        app.register_blueprint(public_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(member_bp)

        app.logger.info("✅ Blueprints erfolgreich registriert.")

    except Exception as e:
        app.logger.error(f"❌ Fehler bei Blueprint-Registrierung: {e}", exc_info=True)

    return app

# Instanziiere die App für WSGI/Gunicorn
app = create_app()
