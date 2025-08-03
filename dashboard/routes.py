import os
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, session, url_for, flash

USERS = {"Burak": "Var", "Marcel": "Mai"}


def login_required(func):
    """Simple login check for dashboard pages."""

    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get("dashboard_user") not in USERS:
            return redirect(url_for("dashboard.login"))
        return func(*args, **kwargs)

    return wrapper


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


@dashboard.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in USERS and USERS[username] == password:
            session["dashboard_user"] = username
            return redirect(url_for("dashboard.guide"))
        flash("Invalid credentials", "danger")
    return render_template("dashboard/login.html")


@dashboard.route("/guide")
@login_required
def guide():
    return render_template("dashboard/guide.html")
