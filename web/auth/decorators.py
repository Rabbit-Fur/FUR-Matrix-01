"""
Role and login decorators for Flask views.

This module provides helpers to ensure a user is logged in and has the
necessary Discord roles stored in the session. Role checks operate on role IDs
so that a user can belong to multiple groups (R3/R4/Admin) simultaneously.
"""

from collections.abc import Iterable
from functools import wraps

from flask import current_app, flash, redirect, session, url_for

import mongo_service
from agents.auth_agent import AuthAgent

from fur_lang.i18n import t


def _agent() -> AuthAgent:
    """Return an ``AuthAgent`` bound to the current session."""

    return AuthAgent(session, mongo_service.db)


def _session_roles() -> list[str]:
    """Return the current user's Discord role IDs as strings.

    ``session['discord_user']['roles']`` may contain integers or strings; this
    helper normalises them into a list of strings. Missing keys result in an
    empty list.
    """

    return [str(role) for role in session.get("discord_user", {}).get("roles", [])]


def _as_list(value) -> list[str]:
    """Normalize a config value into a list of strings.

    Accepts comma separated strings or any iterable of IDs. ``None`` yields an
    empty list.
    """

    if value is None:
        return []
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    if isinstance(value, Iterable):
        return [str(v) for v in value]
    return [str(value)]


def _has_any_required_role(required_ids) -> bool:
    """Check if the session user has at least one of ``required_ids``."""

    session_roles = set(_session_roles())
    required = set(_as_list(required_ids))
    return bool(session_roles & required)


def login_required(view_func):
    """Protect a route for logged in users."""

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
        required = (
            _as_list(current_app.config.get("R3_ROLE_IDS"))
            + _as_list(current_app.config.get("R4_ROLE_IDS"))
            + _as_list(current_app.config.get("ADMIN_ROLE_IDS"))
        )
        if not _has_any_required_role(required):
            flash(t("member_only", default="Members only."))
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapper


def r4_required(view_func):
    """Allow access only for R4 or Admin roles."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        required = _as_list(current_app.config.get("R4_ROLE_IDS")) + _as_list(
            current_app.config.get("ADMIN_ROLE_IDS")
        )
        if not _has_any_required_role(required):
            flash(t("admin_only", default="Admins only."))
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapper


def admin_required(view_func):
    """Allow access only for system administrators."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        required = _as_list(current_app.config.get("ADMIN_ROLE_IDS"))
        if not _has_any_required_role(required):
            flash(t("superuser_only", default="Superuser only."))
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapper
