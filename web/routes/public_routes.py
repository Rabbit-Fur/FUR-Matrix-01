from flask import Blueprint, render_template, abort

public_bp = Blueprint("public", __name__)

@public_bp.route("/")
def landing():
    """Landing Page des Systems."""
    return render_template("public/landing.html")

@public_bp.route("/dashboard")
def dashboard():
    """Öffentliches Dashboard mit Systemstatus/Schnellzugriffen."""
    return render_template("public/dashboard.html")

@public_bp.route("/login")
def login():
    """Login-Seite (Discord oder Formular)."""
    return render_template("public/login.html")

@public_bp.route("/events")
def events_list():
    """Liste aller öffentlichen Events."""
    events = [
        {"id": 1, "title": "Champion Night", "date": "2025-06-01"},
        {"id": 2, "title": "Training", "date": "2025-06-10"}
    ]
    return render_template("public/events_list.html", events=events)

@public_bp.route("/events/<int:event_id>")
def view_event(event_id):
    """Detailansicht für ein bestimmtes Event."""
    if event_id not in (1, 2):
        abort(404)
    event = {"id": event_id, "title": f"Event {event_id}", "date": "2025-06-01", "description": "Details folgen..."}
    return render_template("public/view_event.html", event=event)

@public_bp.route("/hall-of-fame")
def hall_of_fame():
    """Hall of Fame: Champions des Systems."""
    hof = [
        {"username": "Marcel", "month": "Mai 2025", "honor_title": "PvP-Champion", "poster_url": "/static/champions/champion_testchampion_mai2025.png"},
    ]
    return render_template("public/hall_of_fame.html", hof=hof)

@public_bp.route("/leaderboard")
def public_leaderboard():
    """Öffentliches Leaderboard."""
    leaderboard = [
        {"rank": 1, "username": "Marcel", "score": 250},
        {"rank": 2, "username": "Neko", "score": 200},
    ]
    return render_template("public/public_leaderboard.html", leaderboard=leaderboard)

@public_bp.route("/lore")
def lore():
    """Story/Lore-Übersicht."""
    return render_template("public/lore.html")
