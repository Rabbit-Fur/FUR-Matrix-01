"""
web/auth/decorators.py – Rollen- & Login-Decorator für Flask

Dekoratoren für Flask-Views: login_required, r3_required, r4_required.
Stellen sicher, dass der User korrekt eingeloggt ist und die passende Rolle (R3, R4, Admin) hat.
"""

from functools import wraps

from flask import flash, redirect, session, url_for

from fur_lang.i18n import t


def login_required(view_func):
    """Schützt eine Route für eingeloggte User."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            flash(t("login_required"), "warning")
            return redirect(url_for("public.login"))
        return view_func(*args, **kwargs)

    return wrapper


def r3_required(view_func):
    """Zugriff nur für Mitglieder (R3+, Admin)."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if session.get("user", {}).get("role_level") not in ["R3", "R4", "ADMIN"]:
            flash(t("member_access_required"))
            return redirect(url_for("public.login"))
        return view_func(*args, **kwargs)

    return wrapper


def r4_required(view_func):
    """Zugriff nur für R4 oder Admin."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if session.get("user", {}).get("role_level") not in ["R4", "ADMIN"]:
            flash(t("admin_access_required"))
            return redirect(url_for("public.login"))
        return view_func(*args, **kwargs)

    return wrapper


def admin_required(view_func):
    """Zugriff nur für System-Admins."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if session.get("user", {}).get("role_level") != "ADMIN":
            flash(t("superuser_access_required"))
            return redirect(url_for("public.login"))
        return view_func(*args, **kwargs)

    return wrapper
