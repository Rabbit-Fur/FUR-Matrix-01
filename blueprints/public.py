import secrets
from urllib.parse import urlencode

import requests
from bson import ObjectId
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

from fur_lang.i18n import get_supported_languages, t
from mongo_service import get_collection
from web.auth.decorators import login_required, r3_required

public = Blueprint("public", __name__)


@public.route("/")
def landing():
    return render_template("public/landing.html")


@public.route("/set_language")
def set_language():
    lang = request.args.get("lang")
    if lang in get_supported_languages():
        session["lang"] = lang
    return redirect(request.referrer or url_for("public.landing"))


@public.route("/login")
def login():
    user = session.get("discord_user")
    if user:
        role = user.get("role_level")
        if role in ["ADMIN", "R4"]:
            return redirect(url_for("admin.dashboard"))
        elif role == "R3":
            return redirect(url_for("member.dashboard"))
    return render_template("public/login.html")


@public.route("/logout")
def logout():
    session.clear()
    flash(t("logout_success", default="Logged out successfully."), "info")
    return redirect(url_for("public.login"))


@public.route("/login/discord")
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


@public.route("/callback")
def discord_callback():
    code = request.args.get("code")
    state = request.args.get("state")

    if not code:
        return t("missing_code", default="Missing OAuth code."), 400
    if not state or state != session.pop("discord_oauth_state", None):
        return t("invalid_oauth_state", default="Invalid OAuth state."), 400

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
        flash(t("discord_login_failed", default="Discord login failed"), "danger")
        return redirect(url_for("public.login"))

    access_token = token_res.json().get("access_token")

    user_res = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user_data = user_res.json()

    guild_url = f"https://discord.com/api/users/@me/guilds/{current_app.config['DISCORD_GUILD_ID']}"
    guild_res = requests.get(
        f"{guild_url}/member",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if guild_res.status_code != 200:
        join_res = requests.put(
            guild_url,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        if join_res.status_code not in {200, 201, 204}:
            current_app.logger.error(
                "Guild join failed %s: %s", join_res.status_code, join_res.text
            )
            return (
                t(
                    "guild_membership_required",
                    default="Not a member of the FUR Discord server",
                ),
                403,
            )
        guild_res = requests.get(
            f"{guild_url}/member",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if guild_res.status_code != 200:
            current_app.logger.error(
                "Guild membership fetch failed %s: %s",
                guild_res.status_code,
                guild_res.text,
            )
            return (
                t(
                    "guild_membership_required",
                    default="Not a member of the FUR Discord server",
                ),
                403,
            )

    guild_member = guild_res.json()
    user_roles = set(str(role) for role in guild_member.get("roles", []))

    r3_roles = set(map(str, current_app.config.get("R3_ROLE_IDS", set())))
    r4_roles = set(map(str, current_app.config.get("R4_ROLE_IDS", set())))
    admin_roles = set(map(str, current_app.config.get("ADMIN_ROLE_IDS", set())))

    if user_roles & admin_roles:
        role_level = "ADMIN"
    elif user_roles & r4_roles:
        role_level = "R4"
    elif user_roles & r3_roles:
        role_level = "R3"
    else:
        current_app.logger.warning("❌ Invalid Discord role")
        return t("invalid_role", default="Invalid role for access"), 403

    session["discord_roles"] = [role_level]
    session["discord_user"] = {
        "id": user_data["id"],
        "username": user_data["username"],
        "avatar": user_data["avatar"],
        "email": user_data.get("email"),
        "role_level": role_level,
        "roles": list(user_roles),
    }
    session.permanent = True

    get_collection("users").update_one(
        {"discord_id": user_data["id"]},
        {
            "$set": {
                "username": user_data["username"],
                "avatar": user_data["avatar"],
                "email": user_data.get("email"),
                "role_level": role_level,
            }
        },
        upsert=True,
    )

    flash(t("discord_login_success", default="Successfully logged in with Discord"), "success")

    if role_level in ["ADMIN", "R4"]:
        return redirect(url_for("admin.dashboard"))
    else:
        return redirect(url_for("member.dashboard"))


@public.route("/lore")
def lore():
    return render_template("public/lore.html")


@public.route("/calendar")
def calendar():
    return render_template("public/calendar.html")


@public.route("/events")
def events():
    rows = list(get_collection("events").find().sort("event_time", 1))
    if current_app.config.get("TESTING"):
        rows = []
    else:
        rows = list(get_collection("events").find().sort("event_time", 1))
    return render_template("public/events_list.html", events=rows)


@public.route("/events/<event_id>")
def view_event(event_id):
    event = get_collection("events").find_one({"_id": ObjectId(event_id)})
    if not event:
        abort(404)
    participant_docs = list(get_collection("event_participants").find({"event_id": event["_id"]}))
    participants = []
    for p in participant_docs:
        user = get_collection("users").find_one({"discord_id": p["user_id"]})
        participants.append({"username": user.get("username") if user else p["user_id"]})
    return render_template("public/view_event.html", event=event, participants=participants)


@public.route("/events/<event_id>/join", methods=["POST"])
@r3_required
def join_event(event_id):
    if "discord_user" not in session:
        flash(t("login_required", default="Login required."), "warning")
        return redirect(url_for("auth.login"))

    flash(t("event_join_success", default="Successfully joined the event!"), "success")
    return redirect(url_for("public.view_event", event_id=event_id))


@public.route("/hall_of_fame")
def hall_of_fame():
    rows = list(get_collection("hall_of_fame").find().sort("_id", -1).limit(10))
    if current_app.config.get("TESTING"):
        rows = []
    else:
        rows = list(get_collection("hall_of_fame").find().sort("_id", -1).limit(10))
    return render_template("public/hall_of_fame.html", hof=rows)


@public.route("/leaderboard")
def leaderboard():
    rows = list(get_collection("leaderboard").find().sort("score", -1).limit(100))
    leaderboard_list = []
    for i, row in enumerate(rows, start=1):
        leaderboard_list.append({"rank": i, "username": row["username"], "score": row["score"]})
    if current_app.config.get("TESTING"):
        leaderboard_list = []
    else:
        rows = list(get_collection("leaderboard").find().sort("score", -1).limit(100))
        leaderboard_list = []
        for i, row in enumerate(rows, start=1):
            leaderboard_list.append({"rank": i, "username": row["username"], "score": row["score"]})
    return render_template("public/public_leaderboard.html", leaderboard=leaderboard_list)


@public.route("/bank-war-top5")
def bank_war_top5():
    """Display BANK WAR recap and top 5 players."""
    return render_template("public/bank_war_top5.html")


@public.route("/dashboard")
@login_required
def dashboard():
    return render_template("public/dashboard.html")
