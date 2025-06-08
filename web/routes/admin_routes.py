"""
admin_routes.py – Flask Blueprint für Admin-Views (geschützt, R4+)

Stellt alle Admin-Oberflächen bereit, geschützt durch das r4_required-Decorator (nur Admins/R4).
"""

from flask import Blueprint, render_template, Response
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
@admin_bp.route("/create_event")
def create_event():
    """
    Event-Erstellung für Admins.
    """
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

# --- Zusätzliche Admin-Endpoints für Tools & Exporte ---

@admin_bp.route("/trigger_reminder", methods=["POST"])
def trigger_reminder():
    """Löst serverseitig einen Erinnerungs-Task aus (Platzhalter)."""
    return "Reminder triggered"


@admin_bp.route("/trigger_champion_post", methods=["POST"])
def trigger_champion_post():
    """Postet den aktuellen Champion in den Discord-Channel (Platzhalter)."""
    return "Champion post triggered"


@admin_bp.route("/healthcheck", methods=["POST"])
def healthcheck():
    """Einfacher Healthcheck-Endpunkt für Admin-Tools."""
    return Response("ok", status=200)


@admin_bp.route("/export_participants")
def export_participants():
    """CSV-Export aller Teilnehmer (Dummy-Implementierung)."""
    csv_data = "username\n"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=participants.csv"},
    )


@admin_bp.route("/export_scores")
def export_scores():
    """CSV-Export der Score-Tabelle (Dummy-Implementierung)."""
    csv_data = "username,score\n"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=scores.csv"},
    )
