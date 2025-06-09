"""
public_routes.py – Flask Blueprint für alle öffentlichen Views

Stellt alle öffentlichen Seiten bereit (ohne Login/Role), z.B. Landing Page, Login, Lore, Events, Leaderboards.
"""

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    current_app,
    session,
)
from urllib.parse import urlencode
import requests

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
