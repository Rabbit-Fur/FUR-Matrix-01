from flask import Blueprint, render_template

leaderboard_bp = Blueprint("leaderboard", __name__)

@leaderboard_bp.route("/")
def leaderboards():
    """Komplette Leaderboard-Übersicht."""
    return render_template("leaderboard/leaderboards.html")
