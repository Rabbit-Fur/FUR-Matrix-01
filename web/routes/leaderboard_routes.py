from flask import Blueprint, render_template

from web.auth.decorators import r3_required

leaderboard_bp = Blueprint("leaderboard", __name__)


@r3_required
@leaderboard_bp.route("/")
def leaderboards():
    """Komplette Leaderboard-Übersicht."""
    return render_template("leaderboard/leaderboards.html")
