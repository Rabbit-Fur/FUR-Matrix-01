import logging
from datetime import datetime

from bson import ObjectId
from flask import Blueprint, jsonify, request

from mongo_service import get_collection
from schemas.event_schema import EventModel

api_events = Blueprint("api_events", __name__, url_prefix="/api/events")
events = get_collection("events")
log = logging.getLogger(__name__)


def serialize_event(event: dict) -> dict:
    event["id"] = str(event["_id"])
    event.pop("_id", None)
    return event


@api_events.route("/", methods=["GET"])
def get_all_events():
    try:
        data = [serialize_event(e) for e in events.find()]
        return jsonify(data)
    except Exception as e:
        log.error("Failed to fetch events: %s", e)
        return jsonify({"error": str(e)}), 500


@api_events.route("/<event_id>", methods=["GET"])
def get_event(event_id):
    try:
        event = events.find_one({"_id": ObjectId(event_id)})
        if event:
            return jsonify(serialize_event(event))
        return jsonify({"error": "Event not found"}), 404
    except Exception:
        log.exception("Invalid event id %s", event_id)
        return jsonify({"error": "Invalid ObjectId"}), 400


@api_events.route("/", methods=["POST"])
def create_event():
    try:
        data = request.get_json()
        event = EventModel(**data).dict(by_alias=True)
        event["created_at"] = datetime.utcnow()
        event["updated_at"] = datetime.utcnow()
        result = events.insert_one(event)
        event["id"] = str(result.inserted_id)
        return jsonify(event), 201
    except Exception as e:
        log.error("Failed to create event: %s", e)
        return jsonify({"error": str(e)}), 400
