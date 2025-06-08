from flask import Flask, request, session
from flask_babel import Babel


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("config.py")

    Babel(app)

    try:
        # Bestehende Blueprints
        from landing_route import landing_bp
        from static_routes import static_bp
        from healthcheck import health_bp

        # Neue Routengruppen für Blueprint-Integration
        from web.routes.public_routes import public_bp
        from web.routes.member_routes import member_bp
        from web.routes.admin_routes import admin_bp

        # Blueprint-Registrierung
        app.register_blueprint(landing_bp)
        app.register_blueprint(static_bp)
        app.register_blueprint(health_bp)

        app.register_blueprint(public_bp)  # Öffentlich sichtbar
        app.register_blueprint(member_bp, url_prefix="/members")  # restricted
        app.register_blueprint(admin_bp, url_prefix="/admin")     # R4+, Owner

    except Exception as e:
        app.logger.warning(f"Blueprint registration failed: {e}")

    from fur_lang.i18n import t, current_lang

    @app.context_processor
    def inject_i18n_functions():
        return {"t": t, "current_lang": current_lang}

    @app.before_request
    def set_language_from_request():
        lang = request.args.get("lang")
        if lang in app.config.get("BABEL_SUPPORTED_LOCALES", []):
            session["lang"] = lang

    return app
