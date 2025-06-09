"""
member_routes.py – Flask Blueprint für Member-Bereich (R3+)

Stellt alle Views für eingeloggte Mitglieder bereit. Zugriff ist durch r3_required-Decorator geschützt.
"""

from flask import Blueprint, render_template

from web.auth.decorators import r3_required

member_bp = Blueprint("members", __name__)


@r3_required
@member_bp.route("/dashboard")
def dashboard():
    """Mitglieder-Dashboard: Persönliche Infos, Stats, News."""
    return render_template("members/dashboard.html")


@r3_required
@member_bp.route("/downloads")
def downloads():
    """Persönlicher Downloadbereich (Stats, Urkunden)."""
    return render_template("members/downloads.html")


@r3_required
@member_bp.route("/stats")
def stats():
    """Statistiken, Fortschritt, eigene Erfolge."""
    return render_template("members/stats.html")


@r3_required
@member_bp.route("/settings")
def settings():
    """Persönliche Einstellungen für Mitglieder."""
    return render_template("members/settings.html")
