# try/blueprints/api_users.py

from datetime import datetime

from bson import ObjectId
from flask import Blueprint, jsonify, request

from database.mongo_client import db
from schemas.user_schema import UserModel

api_users = Blueprint("api_users", __name__, url_prefix="/api/users")
users = db["users"]


def serialize_user(user) -> dict:
    user["id"] = str(user["_id"])
    del user["_id"]
    return user


@api_users.route("/", methods=["GET"])
def get_all_users():
    return jsonify([serialize_user(u) for u in users.find()])


@api_users.route("/<discord_id>", methods=["GET"])
def get_user_by_discord_id(discord_id):
    user = users.find_one({"discord_id": discord_id})
    if user:
        return jsonify(serialize_user(user))
    return jsonify({"error": "User not found"}), 404


@api_users.route("/", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        user_data = UserModel(**data).dict()
        user_data["created_at"] = datetime.utcnow()
        user_data["updated_at"] = datetime.utcnow()
        result = users.insert_one(user_data)
        user_data["id"] = str(result.inserted_id)
        return jsonify(user_data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
