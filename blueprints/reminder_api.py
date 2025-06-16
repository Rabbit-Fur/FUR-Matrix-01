from flask import Blueprint, jsonify

from bot.reminder_system import send_reminder_by_id
from database.mongo_client import db
from web.auth.decorators import r4_required

reminder_api = Blueprint("reminder_api", __name__)


@reminder_api.route("/<reminder_id>/participants")
@r4_required
def get_participants(reminder_id):
    rows = list(db["reminder_participants"].find({"reminder_id": reminder_id}))
    return jsonify(rows)


@reminder_api.route("/<reminder_id>/send", methods=["POST"])
@r4_required
def send_reminder_now(reminder_id):
    send_reminder_by_id(reminder_id)
    return jsonify({"status": "sent"})


@reminder_api.route("/<reminder_id>/deactivate", methods=["POST"])
@r4_required
def deactivate_reminder(reminder_id):
    db["reminders"].update_one({"_id": reminder_id}, {"$set": {"send_time": None}})
    return jsonify({"status": "deactivated"})
