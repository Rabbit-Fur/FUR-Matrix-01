from flask import Blueprint, render_template

member_bp = Blueprint("members", __name__)

@member_bp.route("/dashboard")
def dashboard():
    """Mitglieder-Dashboard: Persönliche Infos, Stats, News."""
    return render_template("members/dashboard.html")

@member_bp.route("/downloads")
def downloads():
    """Persönlicher Downloadbereich (Stats, Urkunden)."""
    return render_template("members/downloads.html")

@member_bp.route("/stats")
def stats():
    """Statistiken, Fortschritt, eigene Erfolge."""
    return render_template("members/stats.html")

@member_bp.route("/settings")
def settings():
    """Persönliche Einstellungen für Mitglieder."""
    return render_template("members/settings.html")
