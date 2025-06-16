# try/blueprints/api_events.py

from flask import Blueprint, jsonify, request
from database.mongo_client import db
from bson import ObjectId
from datetime import datetime
from schemas.event_schema import EventModel

api_events = Blueprint("api_events", __name__, url_prefix="/api/events")
events = db["events"]

def serialize_event(event):
    event["id"] = str(event["_id"])
    del event["_id"]
    return event

@api_events.route("/", methods=["GET"])
def get_all_events():
    return jsonify([serialize_event(e) for e in events.find()])

@api_events.route("/<event_id>", methods=["GET"])
def get_event(event_id):
    event = events.find_one({"_id": ObjectId(event_id)})
    if event:
        return jsonify(serialize_event(event))
    return jsonify({"error": "Event not found"}), 404

@api_events.route("/", methods=["POST"])
def create_event():
    try:
        data = request.get_json()
        event_data = EventModel(**data).dict()
        event_data["created_at"] = datetime.utcnow()
        event_data["updated_at"] = datetime.utcnow()
        result = events.insert_one(event_data)
        event_data["id"] = str(result.inserted_id)
        return jsonify(event_data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
