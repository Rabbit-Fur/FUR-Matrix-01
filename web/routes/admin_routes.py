<<<<<<< HEAD
"""
admin_routes.py – Flask Blueprint für Admin-Views (geschützt, R4+)

Stellt alle Admin-Oberflächen bereit, geschützt durch das r4_required-Decorator (nur Admins/R4).
"""

from flask import Blueprint, render_template
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
=======
from flask import Blueprint, render_template, abort

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/dashboard")
def dashboard():
    """Admin Dashboard: Systemkontrolle, Logs, Userverwaltung."""
    return render_template("admin/dashboard.html")

@admin_bp.route("/calendar")
def calendar():
    """Admin-Kalenderansicht für Eventplanung."""
    return render_template("admin/calendar.html")

@admin_bp.route("/events")
def events():
    """Admin: Übersicht aller Events (mit Bearbeitung/Export)."""
    return render_template("admin/events.html")

@admin_bp.route("/events/<int:event_id>/edit")
def edit_event(event_id):
    """Bearbeiten eines bestimmten Events (Admin)."""
    if event_id < 1:
        abort(404)
    return render_template("admin/edit_event.html", event_id=event_id)

@admin_bp.route("/events/create")
def create_event():
    """Neues Event als Admin erstellen."""
    return render_template("admin/create_event.html")

@admin_bp.route("/downloads")
def downloads():
    """Downloadbereich für Admin (Statistiken, Logs)."""
    return render_template("admin/downloads.html")

@admin_bp.route("/diplomacy")
def diplomacy():
    """Diplomatie/Allianzenverwaltung (Admin)."""
    return render_template("admin/diplomacy.html")

@admin_bp.route("/leaderboards")
def leaderboards():
    """Admin-Ansicht aller Leaderboards."""
    return render_template("admin/leaderboards.html")

@admin_bp.route("/participants")
def participants():
    """Teilnehmerliste für Events (Admin)."""
    return render_template("admin/participants.html")

@admin_bp.route("/settings")
def settings():
    """Systemweite Admin-Einstellungen."""
    return render_template("admin/settings.html")

@admin_bp.route("/tools")
def tools():
    """Spezielle Admin-Tools (Import/Export/Analyse)."""
    return render_template("admin/tools.html")

@admin_bp.route("/translations_editor")
def translations_editor():
    """Editor für Übersetzungen (i18n Admin)."""
>>>>>>> b9da45a45805ab6a1f5377830ffb553178ced3ba
    return render_template("admin/translations_editor.html")
