from flask import Blueprint, jsonify

from bot.reminder_system import send_reminder_by_id
from web.auth.decorators import r4_required
from database import get_db  # ✅ zentraler DB-Zugriff

reminder_api = Blueprint("reminder_api", __name__, url_prefix="/api/reminders")


@reminder_api.route("/<int:reminder_id>/participants")
@r4_required
def get_participants(reminder_id: int):
    db = get_db()
    rows = db.execute(
        """
        SELECT u.discord_id, u.username
        FROM reminder_participants rp
        JOIN users u ON u.id = rp.user_id
        WHERE rp.reminder_id = ?
        """,
        (reminder_id,),
    ).fetchall()
    return jsonify([dict(row) for row in rows])


@reminder_api.route("/<int:reminder_id>/send", methods=["POST"])
@r4_required
def send_reminder_now(reminder_id: int):
    send_reminder_by_id(reminder_id)
    return jsonify({"status": "sent"})


@reminder_api.route("/<int:reminder_id>/deactivate", methods=["POST"])
@r4_required
def deactivate_reminder(reminder_id: int):
    db = get_db()
    db.execute(
        "UPDATE reminders SET send_time = NULL WHERE id = ?", (reminder_id,)
    )
    db.commit()
    return jsonify({"status": "deactivated"})
