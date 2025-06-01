"""
public_routes.py – Flask Blueprint für alle öffentlichen Views

Stellt alle öffentlichen Seiten bereit (ohne Login/Role), z.B. Landing Page, Login, Lore, Events, Leaderboards.
"""

from flask import Blueprint, render_template

public_bp = Blueprint("public", __name__)

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

@public_bp.route("/lore")
def lore():
    """
    Öffentliche Lore-/Story-Seite.
    """
    return render_template("public/lore.html")

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


@public_bp.route("/events/<int:event_id>/join")
def join_event(event_id):
    if "discord_user_id" not in session:
        return redirect(url_for("public.login"))

    user_id = session["discord_user_id"]
    db = get_db()
    db.execute("INSERT INTO event_participants (event_id, user_id) VALUES (?, ?)", (event_id, user_id))
    db.commit()
    flash(t("you_joined_event"), "success")
    return redirect(url_for("public.view_event", event_id=event_id))
