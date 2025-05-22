"""
web/auth/decorators.py – Rollen- & Login-Decorator für Flask

Dekoratoren für Flask-Views: login_required, r3_required, r4_required.
Stellen sicher, dass der User korrekt eingeloggt ist und die passende Rolle (R3, R4, Admin) hat.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, abort

def login_required(view_func):
    """
    Dekorator: Schützt eine Route, sodass nur eingeloggte User Zugriff haben.

    Falls der User nicht eingeloggt ist, wird er zur Login-Seite weitergeleitet.
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Du musst eingeloggt sein.", "warning")
            return redirect(url_for("public.login"))
        return view_func(*args, **kwargs)
    return wrapper

def r3_required(view_func):
    """
    Dekorator: Zugriff nur für eingeloggte Member (R3, R4, Owner).

    Falls nicht R3 oder höher, Weiterleitung oder 403.
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session or session.get("role") not in ("R3", "R4", "ADMIN", "OWNER"):
            flash("Zugriff nur für eingeloggte Mitglieder.", "warning")
            return redirect(url_for("public.login"))
        return view_func(*args, **kwargs)
    return wrapper

def r4_required(view_func):
    """
    Dekorator: Zugriff nur für R4/Admin/Owner.

    Falls nicht R4/Admin/Owner, Fehler 403.
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session or session.get("role") not in ("R4", "ADMIN", "OWNER"):
            flash("Zugriff nur für Admins.", "danger")
            return abort(403)
        return view_func(*args, **kwargs)
    return wrapper

def admin_required(view_func):
    """
    Dekorator: Zugriff nur für System-Admins/Owner.

    Falls keine ADMIN/OWNER-Rolle, Fehler 403.
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session or session.get("role") not in ("ADMIN", "OWNER"):
            flash("Zugriff nur für System-Admins.", "danger")
            return abort(403)
        return view_func(*args, **kwargs)
    return wrapper
