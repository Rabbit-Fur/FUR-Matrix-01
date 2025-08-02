"""Routes for champion announcements."""

from datetime import datetime

from flask import Blueprint, jsonify, request

import mongo_service
from src.agents.champion_agent import ChampionAgent

champion_blueprint = Blueprint("champion", __name__)


@champion_blueprint.get("/champion")
def get_latest_champion():
    entry = mongo_service.db["hall_of_fame"].find_one(sort=[("created_at", -1)])
    if not entry:
        return jsonify({}), 404
    entry["_id"] = str(entry["_id"])
    return jsonify(entry)


@champion_blueprint.post("/champion")
def add_champion():
    data = request.get_json(force=True) or {}
    username = data.get("username")
    month = data.get("month", datetime.utcnow().strftime("%Y-%m"))
    stats = data.get("stats", "")
    if not username:
        return jsonify({"error": "username required"}), 400
    agent = ChampionAgent(mongo_service.db)
    poster_path = agent.announce_champion(username, month, stats)
    return jsonify({"poster_path": poster_path}), 201
