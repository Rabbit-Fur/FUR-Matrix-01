"""Admin blueprint using MongoDB."""

import json
import os
from datetime import datetime

from bson import ObjectId
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
from werkzeug.utils import secure_filename

from agents.webhook_agent import WebhookAgent
from config import Config
from mongo_service import db
from utils.discord_util import require_roles
from web.auth.decorators import r4_required

admin = Blueprint("admin", __name__)


@require_roles(["R4", "ADMIN"])
@r4_required
@admin.route("/")
def admin_dashboard():
    return render_template("admin/admin.html")


@require_roles(["R4", "ADMIN"])
@r4_required
@admin.route("/calendar")
def calendar():
    return render_template("admin/calendar.html")


@require_roles(["R4", "ADMIN"])
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


@require_roles(["R4", "ADMIN"])
@r4_required
@admin.route("/dashboard")
def dashboard():
    return render_template("admin/dashboard.html")


@require_roles(["R4", "ADMIN"])
@r4_required
@admin.route("/diplomacy")
def diplomacy():
    return render_template("admin/diplomacy.html")


@require_roles(["R4", "ADMIN"])
@r4_required
@admin.route("/downloads")
def downloads():
    return render_template("admin/downloads.html")


@require_roles(["R4", "ADMIN"])
@r4_required
@admin.route("/edit_event", methods=["GET", "POST"])
def edit_event():
    event_id = request.args.get("id") or request.form.get("id")
    if not event_id:
        flash("Unbekanntes Event", "danger")
        return redirect(url_for("admin.events"))

    collection = db["events"]
    event = collection.find_one({"_id": ObjectId(event_id)})
    if not event:
        flash("Unbekanntes Event", "danger")
        return redirect(url_for("admin.events"))

    if request.method == "POST":
        update = {
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "event_date": request.form.get("event_date"),
            "role": request.form.get("role"),
            "recurrence": request.form.get("recurrence"),
            "updated_at": datetime.utcnow(),
        }
        try:
            collection.update_one({"_id": ObjectId(event_id)}, {"$set": update})
            flash("Event aktualisiert", "success")
            return redirect(url_for("admin.events"))
        except Exception as e:
            current_app.logger.error("Event update failed: %s", e, exc_info=True)
            flash("Fehler beim Speichern", "danger")
    return render_template("admin/edit_event.html", event=event)


@require_roles(["R4", "ADMIN"])
@r4_required
@admin.route("/events")
def events():
    rows = list(db["events"].find().sort("event_date", 1))
    for row in rows:
        row["id"] = str(row.get("_id"))
    return render_template("admin/events.html", events=rows)


@require_roles(["R4", "ADMIN"])
@r4_required
@admin.route("/leaderboards")
def leaderboards():
    return render_template("admin/leaderboards.html")


@require_roles(["R4", "ADMIN"])
@r4_required
@admin.route("/participants")
def participants():
    return render_template("admin/participants.html")


@require_roles(["R4", "ADMIN"])
@r4_required
@admin.route("/reminders")
def reminder_admin():
    reminders = list(db["reminders"].find().sort("send_time", 1))
    return render_template("admin/reminders.html", reminders=reminders)


@require_roles(["R4", "ADMIN"])
@r4_required
@admin.route("/settings")
def settings():
    return render_template("admin/settings.html")


@require_roles(["R4", "ADMIN"])
@r4_required
@admin.route("/tools")
def tools():
    return render_template("admin/tools.html")


@require_roles(["R4", "ADMIN"])
@r4_required
@admin.route("/translations_editor", methods=["GET", "POST"])
def translations_editor():
    from fur_lang.i18n import get_supported_languages, translations

    supported_languages = get_supported_languages()
    selected_language = (
        request.args.get("language") or request.form.get("language") or request.args.get("lang")
    )
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
@require_roles(["R4", "ADMIN"])
@r4_required
def trigger_reminder():
    return "Reminder triggered"


@admin.route("/trigger_champion_post", methods=["POST"])
@require_roles(["R4", "ADMIN"])
@r4_required
def trigger_champion_post():
    return "Champion post triggered"


@admin.route("/healthcheck", methods=["POST"])
@require_roles(["R4", "ADMIN"])
@r4_required
def healthcheck():
    return Response("ok", status=200)


@admin.route("/export_participants")
@require_roles(["R4", "ADMIN"])
@r4_required
def export_participants():
    csv_data = "username\n"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=participants.csv"},
    )


@admin.route("/export_scores")
@require_roles(["R4", "ADMIN"])
@r4_required
def export_scores():
    csv_data = "username,score\n"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=scores.csv"},
    )


@admin.route("/events/post/<event_id>", methods=["POST"])
@require_roles(["R4", "ADMIN"])
@r4_required
def post_event(event_id: str):
    """Post an event to Discord via webhook."""
    event = db["events"].find_one({"_id": ObjectId(event_id)})
    if not event:
        flash("Unbekanntes Event", "danger")
        return redirect(url_for("admin.events"))

    content = (
        f"📅 **{event.get('title')}**\n{event.get('description', '')}\n🕒 {event.get('event_date')}"
    )
    webhook = WebhookAgent(Config.DISCORD_WEBHOOK_URL)
    success = webhook.send(content)
    if success:
        flash("Event gepostet", "success")
    else:
        flash("Fehler beim Posten", "danger")
    return redirect(url_for("admin.events"))


@admin.route("/post_champion", methods=["POST"])
@require_roles(["R4", "ADMIN"])
@r4_required
def post_champion():
    from modules.champion import post_champion_poster

    success = post_champion_poster()
    flash(
        "Champion wurde gepostet" if success else "Posten fehlgeschlagen",
        "success" if success else "danger",
    )
    return redirect(url_for("admin.admin_dashboard"))


@admin.route("/post_weekly_report", methods=["POST"])
@require_roles(["R4", "ADMIN"])
@r4_required
def post_weekly_report():
    from modules.weekly_report import post_report

    success = post_report()
    flash(
        "Wochenreport wurde gepostet" if success else "Posten fehlgeschlagen",
        "success" if success else "danger",
    )
    return redirect(url_for("admin.admin_dashboard"))


@admin.route("/post_announcement", methods=["POST"])
@require_roles(["R4", "ADMIN"])
@r4_required
def post_announcement():
    title = request.form.get("title", "").strip()
    message = request.form.get("message", "").strip()

    if not title or not message:
        flash("Titel und Nachricht erforderlich", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    content = f"📣 **{title}**\n{message}"
    success = WebhookAgent(Config.DISCORD_WEBHOOK_URL).send(content)

    flash(
        "Ankündigung gesendet" if success else "Senden fehlgeschlagen",
        "success" if success else "danger",
    )
    return redirect(url_for("admin.admin_dashboard"))


def _allowed_file(filename: str) -> bool:
    """Return True if the filename has an allowed extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]
    )


@admin.route("/upload", methods=["GET", "POST"])
@require_roles(["R4", "ADMIN"])
@r4_required
def upload():
    """Handle file uploads for admin users."""
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    if request.method == "POST":
        if (
            request.content_length
            and request.content_length > current_app.config["MAX_CONTENT_LENGTH"]
        ):
            flash("Datei zu groß", "danger")
            return redirect(request.url)

        file = request.files.get("file")
        if not file or file.filename == "":
            flash("Keine Datei ausgewählt", "danger")
            return redirect(request.url)
        if not _allowed_file(file.filename):
            flash("Ungültiger Dateityp", "danger")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        file.save(os.path.join(upload_folder, filename))
        flash("Datei hochgeladen", "success")
        return redirect(url_for("admin.upload"))

    files = []
    if os.path.exists(upload_folder):
        files = sorted(f for f in os.listdir(upload_folder) if _allowed_file(f))

    return render_template("admin/upload.html", files=files)
