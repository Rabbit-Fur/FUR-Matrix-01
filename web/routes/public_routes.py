"""
public_routes.py – Flask Blueprint für alle öffentlichen Views

Stellt alle öffentlichen Seiten bereit (ohne Login/Role), z.B. Landing Page, Login, Lore, Events, Leaderboards.
"""
import os
from flask import Blueprint, render_template, current_app, request, session, redirect, url_for
from fur_lang.i18n import get_supported_languages

public_bp = Blueprint("public", __name__)

@public_bp.route("/")
def landing():
    print("TEMPLATE_ROOT =", current_app.template_folder)
    print("LANDING_EXISTS =", os.path.exists(os.path.join(current_app.template_folder, "public/landing.html")))
    return render_template("public/landing.html")
#@public_bp.route("/")
#def landing():
#    """
#    Öffentliche Landing Page.
#    """
#    return render_template("public/landing.html")

@public_bp.route("/set_language")
def set_language():
    lang = request.args.get("lang")
    if lang in get_supported_languages():
        session["lang"] = lang
    return redirect(request.referrer or url_for("public_bp.dashboard"))

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
    # DUMMY-DATEN für das Template (kannst du später durch DB/API ersetzen)
    leaderboard = {
        "raids": ["Alice - 120", "Bob - 110", "Charlie - 100"],
        "donations": ["Dino - 500", "Eva - 450"]
    }
    return render_template("public/public_leaderboard.html", leaderboard=leaderboard)


@public_bp.route("/view_event")
def view_event():
    # DUMMY-Event für die Anzeige
    event = {
        "title": "FUR Mega Event",
        "description": "Dies ist nur ein Platzhalter-Event.",
        "start_time": "2025-06-01 20:00",
        "location": "FUR Discord"
    }
    return render_template("public/view_event.html", event=event)

