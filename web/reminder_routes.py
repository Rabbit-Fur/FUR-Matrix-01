"""Routes for reminder scheduling."""

from datetime import datetime

from flask import Blueprint, jsonify, request

import mongo_service
from agents.reminder_agent import ReminderAgent

reminder_blueprint = Blueprint("reminder", __name__)


@reminder_blueprint.get("/reminder")
def list_reminders():
    reminders = []
    for r in mongo_service.db["reminders"].find().sort("remind_at", 1):
        r["_id"] = str(r["_id"])
        reminders.append(r)
    return jsonify(reminders)


@reminder_blueprint.post("/reminder")
def create_reminder():
    data = request.get_json(force=True) or {}
    try:
        remind_at = datetime.fromisoformat(data.get("remind_at"))
    except Exception:
        return jsonify({"error": "invalid remind_at"}), 400
    agent = ReminderAgent(mongo_service.db)
    agent.schedule(int(data.get("user_id", 0)), data.get("message", ""), remind_at)
    return jsonify({"status": "scheduled"})
