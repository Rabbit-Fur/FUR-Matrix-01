"""
admin_routes.py – Flask Blueprint für Admin-Views (geschützt, R4+)

Stellt alle Admin-Oberflächen bereit, geschützt durch das r4_required-Decorator (nur Admins/R4).
"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from init_db_core import get_db_connection
from web.auth.decorators import r4_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@r4_required
@admin_bp.route("/")
def admin_dashboard():
    """
    Zeigt das Admin-Dashboard an.
    """
    return render_template("admin/admin.html")

@r4_required
@admin_bp.route("/calendar")
def calendar():
    """
    Admin-Kalenderansicht.
    """
    return render_template("admin/calendar.html")

@r4_required
@admin_bp.route("/create_event", methods=["GET", "POST"])
def create_event():
    """
    Event-Erstellung für Admins.
    """
    if request.method == "POST":
        title = request.form.get("title")
        event_time = request.form.get("event_time")
        description = request.form.get("description")

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO events (title, event_time, created_by, description) VALUES (?, ?, ?, ?)",
                (title, event_time, 1, description),
            )
            conn.commit()
            conn.close()
            flash("Event erstellt", "success")
            return redirect(url_for("admin.events"))
        except Exception as e:
            flash("Fehler beim Speichern", "danger")

    return render_template("admin/create_event.html")

@r4_required
@admin_bp.route("/dashboard")
def dashboard():
    """
    Alternative Dashboard-Ansicht (z. B. Statistiken).
    """
    return render_template("admin/dashboard.html")

@r4_required
@admin_bp.route("/diplomacy")
def diplomacy():
    """
    Diplomatie-Management.
    """
    return render_template("admin/diplomacy.html")

@r4_required
@admin_bp.route("/downloads")
def downloads():
    """
    Downloads für Admins (z. B. Reports, Templates).
    """
    return render_template("admin/downloads.html")

@r4_required
@admin_bp.route("/edit_event")
def edit_event():
    """
    Event-Bearbeitung.
    """
    return render_template("admin/edit_event.html")

@r4_required
@admin_bp.route("/events")
def events():
    """
    Übersicht aller Events (Verwaltung).
    """
    return render_template("admin/events.html")

@r4_required
@admin_bp.route("/leaderboards")
def leaderboards():
    """
    Leaderboard-Übersicht für Admins.
    """
    return render_template("admin/leaderboards.html")

@r4_required
@admin_bp.route("/participants")
def participants():
    """
    Teilnehmer-Übersicht für Events.
    """
    return render_template("admin/participants.html")

@r4_required
@admin_bp.route("/settings")
def settings():
    """
    Admin-Einstellungen.
    """
    return render_template("admin/settings.html")

@r4_required
@admin_bp.route("/tools")
def tools():
    """
    Admin-Tools (z. B. Import/Export).
    """
    return render_template("admin/tools.html")

@r4_required
@admin_bp.route("/translations_editor")
def translations_editor():
    """
    Editor für Übersetzungen und Internationalisierung.
    """
    return render_template("admin/translations_editor.html")
