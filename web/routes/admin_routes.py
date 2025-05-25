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
    return render_template("admin/translations_editor.html")
