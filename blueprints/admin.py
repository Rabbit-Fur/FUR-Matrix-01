"""Admin blueprint using MongoDB."""

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

from mongo_service import db
from web.auth.decorators import r4_required

admin = Blueprint("admin", __name__)


@r4_required
@admin.route("/")
def admin_dashboard():
    return render_template("admin/admin.html")


@r4_required
@admin.route("/calendar")
def calendar():
    return render_template("admin/calendar.html")


@r4_required
@admin.route("/create_event", methods=["GET", "POST"])
def create_event():
    if request.method == "POST":
        title = request.form.get("title")
        event_time = request.form.get("event_time")
        description = request.form.get("description")
        try:
            db["events"].insert_one(
                {
                    "title": title,
                    "event_time": event_time,
                    "created_by": 1,
                    "description": description,
                }
            )
            flash("Event erstellt", "success")
            return redirect(url_for("admin.events"))
        except Exception as e:
            current_app.logger.error("Event creation failed: %s", e, exc_info=True)
            flash("Fehler beim Speichern", "danger")
    return render_template("admin/create_event.html")


@r4_required
@admin.route("/dashboard")
def dashboard():
    return render_template("admin/dashboard.html")


@r4_required
@admin.route("/diplomacy")
def diplomacy():
    return render_template("admin/diplomacy.html")


@r4_required
@admin.route("/downloads")
def downloads():
    return render_template("admin/downloads.html")


@r4_required
@admin.route("/edit_event")
def edit_event():
    return render_template("admin/edit_event.html")


@r4_required
@admin.route("/events")
def events():
    return render_template("admin/events.html")


@r4_required
@admin.route("/leaderboards")
def leaderboards():
    return render_template("admin/leaderboards.html")


@r4_required
@admin.route("/participants")
def participants():
    return render_template("admin/participants.html")


@r4_required
@admin.route("/reminders")
def reminder_admin():
    reminders = list(db["reminders"].find().sort("send_time", 1))
    return render_template("admin/reminders.html", reminders=reminders)


@r4_required
@admin.route("/settings")
def settings():
    return render_template("admin/settings.html")


@r4_required
@admin.route("/tools")
def tools():
    return render_template("admin/tools.html")


@r4_required
@admin.route("/translations_editor", methods=["GET", "POST"])
def translations_editor():
    from fur_lang.i18n import get_supported_languages, translations

    supported_languages = get_supported_languages()
    selected_language = request.args.get("lang") or request.form.get("language")
    if not selected_language and supported_languages:
        selected_language = supported_languages[0]

    data = {}
    file_path = None
    if selected_language:
        file_path = os.path.join(
            current_app.root_path,
            "translations",
            f"{selected_language}.json",
        )
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    current_app.logger.error("Invalid JSON in %s", file_path)

    if request.method == "POST" and any(k.startswith("translations[") for k in request.form.keys()):
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


@admin.route("/trigger_reminder", methods=["POST"])
def trigger_reminder():
    return "Reminder triggered"


@admin.route("/trigger_champion_post", methods=["POST"])
def trigger_champion_post():
    return "Champion post triggered"


@admin.route("/healthcheck", methods=["POST"])
def healthcheck():
    return Response("ok", status=200)


@admin.route("/export_participants")
def export_participants():
    csv_data = "username\n"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=participants.csv"},
    )


@admin.route("/export_scores")
def export_scores():
    csv_data = "username,score\n"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=scores.csv"},
    )
