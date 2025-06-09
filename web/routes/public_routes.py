"""
public_routes.py – Flask Blueprint für alle öffentlichen Views

Stellt alle öffentlichen Seiten bereit (ohne Login/Role), z.B. Landing Page, Login, Lore, Events, Leaderboards.
"""
import os
from flask import (
    Blueprint,
    render_template,
    current_app,
    request,
    session,
    redirect,
    url_for,
    abort,
    flash,
)
from urllib.parse import urlencode
import requests
from fur_lang.i18n import get_supported_languages

public_bp = Blueprint("public", __name__)

@public_bp.route("/")
def landing():
    return render_template("public/landing.html")

@public_bp.route("/set_language")
def set_language():
    lang = request.args.get("lang")
    if lang in get_supported_languages():
        session["lang"] = lang
    return redirect(request.referrer or url_for("public.landing"))

@public_bp.route("/login")
def login():
    """Login-Seite (öffentlich/Discord)."""
    return render_template("public/login.html")

@public_bp.route("/login/discord")
def discord_login():
    """Startet den OAuth-Login bei Discord."""
    client_id = current_app.config.get("DISCORD_CLIENT_ID")
    redirect_uri = current_app.config.get("DISCORD_REDIRECT_URI")
    if not client_id or not redirect_uri:
        flash("Discord OAuth nicht konfiguriert", "danger")
        return redirect(url_for("public.login"))

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "identify",
    }
    url = f"https://discord.com/oauth2/authorize?{urlencode(params)}"
    return redirect(url)

@public_bp.route("/login/discord/callback")
def discord_callback():
    """Callback-URL für den Discord-OAuth-Login."""
    code = request.args.get("code")
    if not code:
        flash("Discord Login fehlgeschlagen", "danger")
        return redirect(url_for("public.login"))

    try:
        token_resp = requests.post(
            "https://discord.com/api/oauth2/token",
            data={
                "client_id": current_app.config.get("DISCORD_CLIENT_ID"),
                "client_secret": current_app.config.get("DISCORD_CLIENT_SECRET"),
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": current_app.config.get("DISCORD_REDIRECT_URI"),
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        token_resp.raise_for_status()
        access_token = token_resp.json().get("access_token")
    except Exception as e:
        current_app.logger.error(f"Discord Token Error: {e}")
        flash("Discord Login fehlgeschlagen", "danger")
        return redirect(url_for("public.login"))

    try:
        user_resp = requests.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        user_resp.raise_for_status()
        user = user_resp.json()
    except Exception as e:
        current_app.logger.error(f"Discord User Error: {e}")
        flash("Discord Login fehlgeschlagen", "danger")
        return redirect(url_for("public.login"))

    session["discord_user_id"] = user["id"]
    session["discord_username"] = user.get("username")
    flash("Erfolgreich mit Discord eingeloggt", "success")
    return redirect(url_for("public.landing"))

@public_bp.route("/lore")
def lore():
    """Story/Lore-Übersicht."""
    return render_template("public/lore.html")

@public_bp.route("/calendar")
def calendar():
    """Öffentlicher Event-Kalender."""
    return render_template("public/calendar.html")

@public_bp.route("/events")
def events():
    """Liste aller öffentlichen Events."""
    # DUMMY-Daten – später mit Datenbank/Logik ersetzen
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

@public_bp.route("/events/<int:event_id>/join", methods=["POST"])
def join_event(event_id):
    """Ermöglicht das Beitreten zu einem Event (Dummy, Demo-Logik)."""
    # Beispiel: Session-User in participants eintragen (hier nur Flash-Meldung als Dummy)
    flash("Du bist dem Event erfolgreich beigetreten!", "success")
    return redirect(url_for('public.view_event', event_id=event_id))

@public_bp.route("/hall_of_fame")
def hall_of_fame():
    """Hall of Fame: Champions des Systems."""
    hof = [
        {"username": "Marcel", "month": "Mai 2025", "honor_title": "PvP-Champion", "poster_url": "/static/champions/champion_testchampion_mai2025.png"},
    ]
    return render_template("public/hall_of_fame.html", hof=hof)

@public_bp.route("/leaderboard")
def leaderboard():
    """Öffentliches Leaderboard."""
    leaderboard_data = [
        {"rank": 1, "username": "Marcel", "score": 250},
        {"rank": 2, "username": "Neko", "score": 200},
    ]
    return render_template("public/public_leaderboard.html", leaderboard=leaderboard_data)

@public_bp.route("/dashboard")
def dashboard():
    """Öffentliches Dashboard mit Systemstatus/Schnellzugriffen."""
    return render_template("public/dashboard.html")
