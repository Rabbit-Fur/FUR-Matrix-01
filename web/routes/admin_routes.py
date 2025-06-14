"""
admin_routes.py – Flask Blueprint für Admin-Views (geschützt, R4+)

Stellt alle Admin-Oberflächen bereit, geschützt durch das r4_required-Decorator (nur Admins/R4).
"""

import json
import os

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from init_db_core import get_db_connection
from web.auth.decorators import r4_required
from web.database import get_db

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
            current_app.logger.error("Event creation failed: %s", e, exc_info=True)
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
@admin_bp.route("/reminders")
def reminder_admin():
    db = get_db()
    reminders = db.execute("SELECT * FROM reminders ORDER BY send_time ASC").fetchall()
    db.close()
    return render_template("admin/reminders.html", reminders=reminders)


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
@admin_bp.route("/translations_editor", methods=["GET", "POST"])
def translations_editor():
    """Editor für Übersetzungen und Internationalisierung."""

    from fur_lang.i18n import get_supported_languages, translations

    supported_languages = get_supported_languages()
    selected_language = request.args.get("lang") or request.form.get("language")
    if not selected_language and supported_languages:
        selected_language = supported_languages[0]

    data = {}
    file_path = None
    if selected_language:
        file_path = os.path.join(
            current_app.root_path, "translations", f"{selected_language}.json"
        )
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    current_app.logger.error("Invalid JSON in %s", file_path)

    if request.method == "POST" and any(
        k.startswith("translations[") for k in request.form.keys()
    ):
        updated = {}
        for k, v in request.form.items():
            if k.startswith("translations[") and k.endswith("]"):
                key = k[len("translations[") : -1]
                updated[key] = v
        if file_path:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(updated, f, indent=2, ensure_ascii=False)
            translations[selected_language] = updated
            data = updated

    return render_template(
        "admin/translations_editor.html",
        available_languages=supported_languages,
        selected_language=selected_language,
        translations=data,
    )


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
