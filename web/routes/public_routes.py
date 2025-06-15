# public_routes.py – Discord Login & öffentliche Views für das FUR System

import os
import secrets
from urllib.parse import urlencode

import requests
from flask import (
    Blueprint, abort, current_app, flash, redirect,
    render_template, request, session, url_for
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
    user = session.get("user")
    if user:
        role = user.get("role_level")
        if role in ["ADMIN", "R4"]:
            return redirect(url_for("admin.dashboard"))
        elif role == "R3":
            return redirect(url_for("member.dashboard"))
    return render_template("public/login.html")


@public_bp.route("/logout")
def logout():
    session.clear()
    flash("Du wurdest erfolgreich ausgeloggt.", "info")
    return redirect(url_for("public.login"))


@public_bp.route("/login/discord")
def discord_login():
    client_id = current_app.config["DISCORD_CLIENT_ID"]
    redirect_uri = current_app.config["DISCORD_REDIRECT_URI"]

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
    code = request.args.get("code")
    state = request.args.get("state")

    if not code:
        return "Fehlender Code", 400
    if not state or state != session.pop("discord_oauth_state", None):
        return "Ungültiger OAuth-State", 400

    # Token anfordern
    token_res = requests.post(
        "https://discord.com/api/oauth2/token",
        data={
            "client_id": current_app.config["DISCORD_CLIENT_ID"],
            "client_secret": current_app.config["DISCORD_CLIENT_SECRET"],
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": current_app.config["DISCORD_REDIRECT_URI"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )

    if token_res.status_code != 200:
        current_app.logger.error("OAuth Token Error %s: %s", token_res.status_code, token_res.text)
        flash("Discord Login fehlgeschlagen", "danger")
        return redirect(url_for("public.login"))

    access_token = token_res.json().get("access_token")

    # User-Daten holen
    user_res = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user_data = user_res.json()

    # Mitgliedschaft im FUR-Server prüfen
    guild_res = requests.get(
        f"https://discord.com/api/users/@me/guilds/{current_app.config['DISCORD_GUILD_ID']}/member",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if guild_res.status_code != 200:
        return "Nicht-Mitglied im FUR Discord-Server", 403

    guild_member = guild_res.json()
    user_roles = set(str(role) for role in guild_member.get("roles", []))

    r3_roles = set(map(str, current_app.config.get("R3_ROLE_IDS", set())))
    r4_roles = set(map(str, current_app.config.get("R4_ROLE_IDS", set())))
    admin_roles = set(map(str, current_app.config.get("ADMIN_ROLE_IDS", set())))

    current_app.logger.info(f"Discord User Rollen: {user_roles}")
    current_app.logger.info(f"Vergleichsrollen → R3: {r3_roles}, R4: {r4_roles}, ADMIN: {admin_roles}")

    if user_roles & admin_roles:
        role_level = "ADMIN"
    elif user_roles & r4_roles:
        role_level = "R4"
    elif user_roles & r3_roles:
        role_level = "R3"
    else:
        current_app.logger.warning("❌ Keine gültige Discord-Rolle erkannt.")
        return "Keine gültige Rolle für den Zugriff", 403

    # Session speichern
    session["user"] = {
        "id": user_data["id"],
        "username": user_data["username"],
        "avatar": user_data["avatar"],
        "email": user_data.get("email"),
        "role_level": role_level,
    }
    session.permanent = True  # Session für 1 Tag aktiv

    # Persistenz in DB
    from database import get_db
    db = get_db()
    db.execute("""
        INSERT INTO users (discord_id, username, avatar, email, role_level)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(discord_id) DO UPDATE SET
            username=excluded.username,
            avatar=excluded.avatar,
            email=excluded.email,
            role_level=excluded.role_level
    """, (
        user_data["id"],
        user_data["username"],
        user_data["avatar"],
        user_data.get("email"),
        role_level
    ))
    db.commit()

    # Weiterleitung je nach Rolle
    flash("Erfolgreich mit Discord eingeloggt", "success")

    if role_level in ["ADMIN", "R4"]:
        return redirect(url_for("admin.dashboard"))
    else:
        return redirect(url_for("member.dashboard"))


# Weitere öffentliche Routen
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
