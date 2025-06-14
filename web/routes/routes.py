import datetime

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

public = Blueprint("public", __name__)
members = Blueprint("members", __name__)


# Utils für Language Switch und User
def get_user():
    # Beispiel-Dummy, hier kannst du später echte Auth einbauen
    return session.get("user")


@public.before_app_request
def before_request():
    g.lang = request.args.get("lang", session.get("lang", "de"))
    g.user = get_user()
    g.current_year = datetime.datetime.now().year


# ---------- Public Routes ----------


@public.route("/")
def landing():
    return render_template("landing.html")


@public.route("/events")
def events_list():
    # Dummy-Events, später aus DB laden!
    events = [
        {"id": 1, "title": "Champion Night", "event_time": "2025-06-01 20:00"},
        {"id": 2, "title": "Training", "event_time": "2025-06-10 19:30"},
    ]
    return render_template("events_list.html", events=events)


@public.route("/events/<int:event_id>")
def view_event(event_id):
    # Dummy-Event, später aus DB!
    event = {
        "id": event_id,
        "title": f"Event {event_id}",
        "event_time": "2025-06-01 20:00",
        "description": "Details folgen...",
        "role": "Mitglied",
    }
    participants = [
        {"username": "Marcel", "checked_in": True},
        {"username": "Evernight", "checked_in": False},
    ]
    return render_template("view_event.html", event=event, participants=participants)


@public.route("/hall-of-fame")
def hall_of_fame():
    hof = [
        {
            "username": "Marcel",
            "month": "Mai 2025",
            "honor_title": "PvP-Champion",
            "poster_url": "/static/champions/champion_testchampion_mai2025.png",
        },
    ]
    return render_template("hall_of_fame.html", hof=hof)


@public.route("/leaderboard")
def public_leaderboard():
    leaderboard = [
        {"rank": 1, "username": "Marcel", "score": 250},
        {"rank": 2, "username": "Neko", "score": 200},
    ]
    return render_template("leaderboard.html", leaderboard=leaderboard)


@public.route("/lore")
def lore():
    return render_template("lore.html")


@public.route("/login")
def login():
    return render_template("login.html")


@public.route("/login/discord")
def discord_login():
    flash("Discord Login: Noch nicht implementiert!", "info")
    return redirect(url_for("public.login"))


# ---------- Members Routes ----------


@members.route("/downloads")
def downloads():
    return render_template("downloads.html")


@members.route("/stats")
def stats():
    return render_template("stats.html")


# Optional: Weitere Member-Routen wie Einstellungen, Profil etc.

# ---------- Kalender ----------


@public.route("/calendar")
def calendar():
    # Dummy-Daten; FullCalendar erwartet Events als JSON-Liste
    events_json = '[{"title": "Champion Night", "start": "2025-06-01"}]'
    return render_template("calendar.html", events_json=events_json)
