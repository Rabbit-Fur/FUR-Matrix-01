"""Role and login decorators for Flask views."""

from functools import wraps
from typing import Iterable

from flask import abort, current_app, redirect, request, session, url_for


def _as_list(value: Iterable | str | None) -> list[str]:
    """Return *value* as a list of strings."""

    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(v) for v in value]
    return [v.strip() for v in str(value).split(",") if v.strip()]


def _config_ids(key: str) -> set[str]:
    """Return configured role IDs for *key* from ``current_app.config``."""

    return set(_as_list(current_app.config.get(key)))


def _session_roles() -> set[str]:
    """Return the current user's role IDs from the session."""

    return set(_as_list(session.get("discord_roles", [])))


def _role_required(config_key: str | None):
    """Internal decorator factory checking login and optional roles."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if "discord_user" not in session:
                try:
                    next_url = request.full_path if request.query_string else request.path
                    return redirect(url_for("auth.login", next=next_url))
                except Exception:  # pragma: no cover - no auth blueprint
                    abort(401)

            if config_key:
                required = _config_ids(config_key)
                if not (_session_roles() & required):
                    abort(403)

            return view_func(*args, **kwargs)

        return wrapper

    return decorator


def login_required(view_func):
    return _role_required(None)(view_func)


def r3_required(view_func):
    return _role_required("R3_ROLE_IDS")(view_func)


def r4_required(view_func):
    return _role_required("R4_ROLE_IDS")(view_func)


def admin_required(view_func):
    return _role_required("ADMIN_ROLE_IDS")(view_func)
