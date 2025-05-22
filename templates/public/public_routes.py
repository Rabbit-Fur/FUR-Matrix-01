"""
public_routes.py – Flask Blueprint für alle öffentlichen (nicht eingeloggten) Views

Stellt alle öffentlichen Seiten wie Landing, Login, Events, Hall of Fame, Leaderboards und Lore bereit.
"""

from flask import Blueprint, render_template

public_bp = Blueprint("public", __name__, template_folder="templates")

@public_bp.route("/")
def landing():
    """
    Öffentliche Landing Page.
    """
    return render_template("public/landing.html")

@public_bp.route("/login")
def login():
    """
    Login-Seite (öffentlich).
    """
    return render_template("public/login.html")

@public_bp.route("/calendar")
def calendar():
    """
    Öffentlicher Event-Kalender.
    """
    return render_template("public/calendar.html")

@public_bp.route("/events_list")
def events_list():
    """
    Öffentliche Event-Liste.
    """
    return render_template("public/events_list.html")

@public_bp.route("/hall_of_fame")
def hall_of_fame():
    """
    Öffentliche Hall of Fame.
    """
    return render_template("public/hall_of_fame.html")

@public_bp.route("/lore")
def lore():
    """
    Öffentliche Lore-/Story-Seite.
    """
    return render_template("public/lore.html")

@public_bp.route("/public_leaderboard")
def public_leaderboard():
    """
    Öffentliche Leaderboard-Seite.
    """
    return render_template("public/public_leaderboard.html")

@public_bp.route("/view_event")
def view_event():
    """
    Öffentliche Detailansicht eines Events.
    """
    return render_template("public/view_event.html")
