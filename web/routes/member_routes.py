"""
member_routes.py – Flask Blueprint für Member-Bereich (R3+)

Stellt alle Views für eingeloggte Mitglieder bereit. Zugriff ist durch r3_required-Decorator geschützt.
"""

from flask import Blueprint, render_template
from web.auth.decorators import r3_required

member_bp = Blueprint("member", __name__, url_prefix="/members")

@r3_required
@member_bp.route("/member_dashboard")
def member_dashboard():
    """
    Zeigt das Member-Dashboard (Startseite nach Login).
    """
    return render_template("member/member_dashboard.html")

@r3_required
@member_bp.route("/member_downloads")
def member_downloads():
    """
    Download-Bereich für Mitglieder.
    """
    return render_template("member/member_downloads.html")

@r3_required
@member_bp.route("/member_stats")
def member_stats():
    """
    Zeigt die Statistiken für das eingeloggte Mitglied.
    """
    return render_template("member/member_stats.html")

@r3_required
@member_bp.route("/settings")
def settings():
    """
    Persönliche Einstellungen für Mitglieder.
    """
    return render_template("member/settings.html")
