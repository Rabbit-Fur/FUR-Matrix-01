from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Blueprint-Registrierungen
from blueprints.public_routes import public_bp
from blueprints.admin_routes import admin_bp
from blueprints.member_routes import member_bp

app.register_blueprint(public_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(member_bp)