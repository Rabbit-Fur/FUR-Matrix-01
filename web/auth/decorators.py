"""
web/auth/decorators.py – Rollen- & Login-Decorator für Flask

Dekoratoren für Flask-Views: login_required, r3_required, r4_required.
Stellen sicher, dass der User korrekt eingeloggt ist und die passende Rolle (R3, R4, Admin) hat.
"""

from functools import wraps

from flask import flash, redirect, session, url_for

import mongo_service
from agents.auth_agent import AuthAgent

from fur_lang.i18n import t


def _agent():
    return AuthAgent(session, mongo_service.db)


def login_required(view_func):
    """Schützt eine Route für eingeloggte User."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not _agent().is_logged_in():
            flash(t("login_required", default="Login required."), "warning")
            return redirect(url_for("public.login"))
        return view_func(*args, **kwargs)

    return wrapper


def r3_required(view_func):
    """Zugriff nur für Mitglieder (R3+, Admin)."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not _agent().is_r3():
            flash(t("member_only", default="Members only."))
            return redirect(url_for("public.login"))
        return view_func(*args, **kwargs)

    return wrapper


def r4_required(view_func):
    """Zugriff nur für R4 oder Admin."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not _agent().is_r4():
            flash(t("admin_only", default="Admins only."))
            return redirect(url_for("public.login"))
        return view_func(*args, **kwargs)

    return wrapper


def admin_required(view_func):
    """Zugriff nur für System-Admins."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not _agent().is_admin():
            flash(t("superuser_only", default="Superuser only."))
            return redirect(url_for("public.login"))
        return view_func(*args, **kwargs)

    return wrapper
