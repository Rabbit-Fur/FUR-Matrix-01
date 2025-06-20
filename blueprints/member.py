"""Member routes protected by the ``r3_required`` decorator."""

from flask import Blueprint, render_template

from utils.discord_util import require_roles
from web.auth.decorators import r3_required

member = Blueprint("member", __name__)


@require_roles(["R3", "R4", "ADMIN"])
@r3_required
@member.route("/dashboard")
def dashboard():
    """Mitglieder-Dashboard: Persönliche Infos, Stats, News."""
    return render_template("members/dashboard.html")


@require_roles(["R3", "R4", "ADMIN"])
@r3_required
@member.route("/downloads")
def downloads():
    """Persönlicher Downloadbereich (Stats, Urkunden)."""
    return render_template("members/downloads.html")


@require_roles(["R3", "R4", "ADMIN"])
@r3_required
@member.route("/stats")
def stats():
    """Statistiken, Fortschritt, eigene Erfolge."""
    return render_template("members/stats.html")


@require_roles(["R3", "R4", "ADMIN"])
@r3_required
@member.route("/settings")
def settings():
    """Persönliche Einstellungen für Mitglieder."""
    return render_template("members/settings.html")
