"""
web/__init__.py – Flask Application Factory für FUR SYSTEM
"""
import os
from flask import Flask
from flask_babel import Babel
from config import Config

def create_app():
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_folder = os.path.join(base_dir, "templates")
    app = Flask(__name__,
            template_folder=template_folder,
            static_folder=os.path.join(base_dir, "static"))

    app.config.from_object(Config)

    # Flask-Babel für Mehrsprachigkeit
    app.config.setdefault("BABEL_DEFAULT_LOCALE", "de")
    app.config.setdefault("BABEL_TRANSLATION_DIRECTORIES", os.path.join(base_dir, "translations"))
    babel = Babel(app)

    try:
        from web.routes.public_routes import public_bp
        from web.routes.member_routes import member_bp
        from web.routes.admin_routes import admin_bp
        # Optional: from web.routes.leaderboard_routes import leaderboard_bp

        app.register_blueprint(public_bp)
        app.register_blueprint(member_bp, url_prefix="/members")
        app.register_blueprint(admin_bp, url_prefix="/admin")
        # app.register_blueprint(leaderboard_bp, url_prefix="/leaderboard")

        app.logger.info("✅ Alle Blueprints erfolgreich registriert.")

    except Exception as e:
        app.logger.error(f"Blueprint registration failed: {e}", exc_info=True)

    if not os.path.exists(os.path.join(app.template_folder, "public/landing.html")):
        app.logger.error("❌ landing.html nicht gefunden! Kontrolliere den Pfad.")

    return app
