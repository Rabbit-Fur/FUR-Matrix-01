"""Authentication and role-based decorators for Flask views."""

from collections.abc import Iterable
from functools import wraps

from flask import current_app, flash, redirect, request, session, url_for

import mongo_service
from agents.auth_agent import AuthAgent
from fur_lang.i18n import t


def _agent() -> AuthAgent:
    """Return an ``AuthAgent`` bound to the current session."""
    return AuthAgent(session, mongo_service.db)


def _as_list(value: Iterable | str | None) -> list[str]:
    """Normalize a value into a list of strings."""
    if value is None:
        return []
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    if isinstance(value, Iterable):
        return [str(v) for v in value]
    return [str(value)]


def _config_ids(key: str) -> set[str]:
    """Return configured role IDs for *key* from ``current_app.config``."""
    return set(_as_list(current_app.config.get(key)))


def _session_roles() -> set[str]:
    """Return the current user's role IDs from the session."""
    return set(_as_list(session.get("discord_roles", [])))


def _has_any_required_role(required_ids) -> bool:
    """Check if the session user has at least one of ``required_ids``."""
    return bool(_session_roles() & set(_as_list(required_ids)))


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
        required = (
            _config_ids("R3_ROLE_IDS") | _config_ids("R4_ROLE_IDS") | _config_ids("ADMIN_ROLE_IDS")
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
        required = _config_ids("R4_ROLE_IDS") | _config_ids("ADMIN_ROLE_IDS")
        if not _has_any_required_role(required):
            flash(t("admin_only", default="Admins only."))
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapper


def admin_required(view_func):
    """Allow access only for system administrators."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        required = _config_ids("ADMIN_ROLE_IDS")
        if not _has_any_required_role(required):
            flash(t("superuser_only", default="Superuser only."))
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapper


__all__ = ["login_required", "r3_required", "r4_required", "admin_required"]
