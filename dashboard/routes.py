from flask import Blueprint, render_template
import os
from datetime import datetime
from dashboard.routes import dashboard
app.register_blueprint(dashboard)

dashboard = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@dashboard.route("/progress")
def progress():
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = f"core/logs/{today}-daily.md"
    log_content = ""
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            log_content = f.read()
    return render_template("dashboard/progress.html", log_content=log_content)
