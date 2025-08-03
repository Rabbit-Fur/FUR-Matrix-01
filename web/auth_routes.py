import secrets
from urllib.parse import urlencode

import requests
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from fur_lang.i18n import t
from mongo_service import get_collection

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login():
    user = session.get("discord_user")
    if user:
        role = user.get("role_level")
        if role in ["ADMIN", "R4"]:
            return redirect(url_for("admin.dashboard"))
        if role == "R3":
            return redirect(url_for("member.dashboard"))
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


@auth_bp.route("/callback")
def callback():
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
        return redirect(url_for("auth.login"))
    access_token = token_res.json().get("access_token")
    user_res = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user_data = user_res.json()
    guild_res = requests.get(
        f"https://discord.com/api/users/@me/guilds/{current_app.config['DISCORD_GUILD_ID']}/member",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if guild_res.status_code != 200:
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
    return redirect(url_for("member.dashboard"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash(t("logout_success", default="Logged out successfully."), "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/dashboard")
def dashboard():
    return render_template("public/dashboard.html")


@auth_bp.route("/admin")
def admin():
    return redirect(url_for("admin.dashboard"))
