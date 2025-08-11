from flask import Blueprint, request, jsonify
import logging

reminder_bp = Blueprint('reminder', __name__)

@reminder_bp.route('/remind', methods=['POST'])
def remind():
    try:
        data = request.json
        user = data.get("user")
        message = t(data.get("message", "Erinnerung"))
        # Reminder-Logik...
        logging.info(f"Reminder send to {user}: {message}")
        return jsonify({"msg": t("Reminder sent successfully!")}), 200
    except Exception as e:
        logging.error(f"Reminder API Error: {e}")
        return jsonify({"error": t("Reminder failed"), "details": str(e)}), 500
