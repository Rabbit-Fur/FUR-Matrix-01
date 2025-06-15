"""
public_routes.py – Flask Blueprint für alle öffentlichen Views

Stellt alle öffentlichen Seiten bereit (ohne Login/Role), z.B. Landing Page, Login, Lore, Events, Leaderboards.
"""

import os
import secrets
from urllib.parse import urlencode

import requests
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from fur_lang.i18n import get_supported_languages
from web.auth.decorators import r3_required

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
    client_id = current_app.config.get("DISCORD_CLIENT_ID")
    redirect_uri = current_app.config.get("DISCORD_REDIRECT_URI")

    if not client_id or not redirect_uri:
        flash("Discord OAuth nicht konfiguriert", "danger")
        return redirect(url_for("public.login"))

    state = secrets.token_urlsafe(16)
    session["discord_oauth_state"] = state

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "identify guilds guilds.members.read",
        "state": state,
    }

    url = f"https://discord.com/oauth2/authorize?{urlencode(params)}"
    return redirect(url)



@public_bp.route("/callback")
def discord_callback():
    """Callback-URL für den Discord-OAuth-Login (einheitlich genutzt)."""
    code = request.args.get("code")
    state = request.args.get("state")

    if not code:
        return "Fehlender Code", 400
    if not state or state != session.pop("discord_oauth_state", None):
        return "Ungültiger OAuth-State", 400

    data = {
        "client_id": current_app.config.get("DISCORD_CLIENT_ID"),
        "client_secret": current_app.config.get("DISCORD_CLIENT_SECRET"),
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": current_app.config.get("DISCORD_REDIRECT_URI"),
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_response = requests.post(
        "https://discord.com/api/oauth2/token",
        data=data,
        headers=headers,
        timeout=10,
    )

    if token_response.status_code != 200:
        current_app.logger.error(
            "Discord Token Error %s - %s",
            token_response.status_code,
            token_response.text,
        )
        flash("Discord Login fehlgeschlagen", "danger")
        return redirect(url_for("public.login"))

    access_token = token_response.json().get("access_token")

    user_response = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user_data = user_response.json()

    guild_response = requests.get(
        f"https://discord.com/api/users/@me/guilds/{current_app.config.get('DISCORD_GUILD_ID')}/member",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if guild_response.status_code != 200:
        return "Nicht-Mitglied im FUR Discord-Server", 403

    guild_member = guild_response.json()
    user_roles = set(guild_member.get("roles", []))

    r3_roles = current_app.config.get("R3_ROLE_IDS")
    r4_roles = current_app.config.get("R4_ROLE_IDS")
    admin_roles = current_app.config.get("ADMIN_ROLE_IDS")

    if user_roles & admin_roles:
        role_level = "ADMIN"
    elif user_roles & r4_roles:
        role_level = "R4"
    elif user_roles & r3_roles:
        role_level = "R3"
    else:
        return "Keine gültige Rolle für den Zugriff", 403

    session["user"] = {
        "id": user_data["id"],
        "username": user_data["username"],
        "avatar": user_data["avatar"],
        "email": user_data.get("email"),
        "role_level": role_level,
    }

    flash("Erfolgreich mit Discord eingeloggt", "success")
    return redirect(url_for("dashboard.progress"))


@public_bp.route("/lore")
def lore():
    return render_template("public/lore.html")


@public_bp.route("/calendar")
def calendar():
    return render_template("public/calendar.html")


@public_bp.route("/events")
def events():
    events = [
        {"id": 1, "title": "Champion Night", "date": "2025-06-01"},
        {"id": 2, "title": "Training", "date": "2025-06-10"},
    ]
    return render_template("public/events_list.html", events=events)


@public_bp.route("/events/<int:event_id>")
def view_event(event_id):
    if event_id not in (1, 2):
        abort(404)
    event = {
        "id": event_id,
        "title": f"Event {event_id}",
        "date": "2025-06-01",
        "description": "Details folgen...",
    }
    return render_template("public/view_event.html", event=event)


@public_bp.route("/events/<int:event_id>/join", methods=["POST"])
@r3_required
def join_event(event_id):
    if "user" not in session:
        flash("Du musst eingeloggt sein.", "warning")
        return redirect(url_for("public.login"))

    flash("Du bist dem Event erfolgreich beigetreten!", "success")
    return redirect(url_for("public.view_event", event_id=event_id))


@public_bp.route("/hall_of_fame")
def hall_of_fame():
    hof = [
        {
            "username": "Marcel",
            "month": "Mai 2025",
            "honor_title": "PvP-Champion",
            "poster_url": "/static/champions/champion_testchampion_mai2025.png",
        },
    ]
    return render_template("public/hall_of_fame.html", hof=hof)


@public_bp.route("/leaderboard")
def leaderboard():
    leaderboard_data = [
        {"rank": 1, "username": "Marcel", "score": 250},
        {"rank": 2, "username": "Neko", "score": 200},
    ]
    return render_template("public/public_leaderboard.html", leaderboard=leaderboard_data)


@public_bp.route("/dashboard")
def dashboard():
    return render_template("public/dashboard.html")
