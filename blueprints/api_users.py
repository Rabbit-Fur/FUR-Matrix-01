import logging
from datetime import datetime

from flask import Blueprint, jsonify, request

from mongo_service import get_collection
from schemas.user_schema import UserModel

api_users = Blueprint("api_users", __name__, url_prefix="/api/users")
users = get_collection("users")
log = logging.getLogger(__name__)


def serialize_user(user: dict) -> dict:
    user["id"] = str(user["_id"])
    user.pop("_id", None)
    return user


@api_users.route("/", methods=["GET"])
def get_all_users():
    try:
        data = [serialize_user(u) for u in users.find()]
        return jsonify(data)
    except Exception as e:
        log.error("Failed to list users: %s", e)
        return jsonify({"error": str(e)}), 500


@api_users.route("/<discord_id>", methods=["GET"])
def get_user_by_discord_id(discord_id):
    try:
        user = users.find_one({"discord_id": discord_id})
        if user:
            return jsonify(serialize_user(user))
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        log.error("Failed to load user %s: %s", discord_id, e)
        return jsonify({"error": str(e)}), 400


@api_users.route("/", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        user = UserModel(**data).dict(by_alias=True)
        user["created_at"] = datetime.utcnow()
        user["updated_at"] = datetime.utcnow()
        result = users.insert_one(user)
        user["id"] = str(result.inserted_id)
        return jsonify(user), 201
    except Exception as e:
        log.error("Failed to create user: %s", e)
        return jsonify({"error": str(e)}), 400
