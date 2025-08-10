"""Authentication and role-based decorators for Flask views."""

from functools import wraps

from flask import flash, redirect, session, url_for

import mongo_service
from agents.auth_agent import AuthAgent
from fur_lang.i18n import t


def _agent() -> AuthAgent:
    return AuthAgent(session, mongo_service.db)


def login_required(view_func):
    """Protect a route for logged-in users."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not _agent().is_logged_in() or "discord_user" not in session:
            flash(t("login_required", default="Login required."), "warning")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapper


def r3_required(view_func):
    """Allow access only for members (R3+, Admin)."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not _agent().is_r3() or session.get("discord_user", {}).get("role_level") not in [
            "R3",
            "R4",
            "ADMIN",
        ]:
            flash(t("member_only", default="Members only."))
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapper


def r4_required(view_func):
    """Allow access only for R4 or Admin."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not _agent().is_r4() or session.get("discord_user", {}).get("role_level") not in [
            "R4",
            "ADMIN",
        ]:
            flash(t("admin_only", default="Admins only."))
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapper


def admin_required(view_func):
    """Allow access only for system admins."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not _agent().is_admin() or session.get("discord_user", {}).get("role_level") != "ADMIN":
            flash(t("superuser_only", default="Superuser only."))
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapper


__all__ = ["login_required", "r3_required", "r4_required", "admin_required"]
