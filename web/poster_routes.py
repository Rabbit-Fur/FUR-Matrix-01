"""Routes for poster handling."""

from pathlib import Path

from flask import Blueprint, jsonify, request, send_from_directory

from agents.poster_agent import PosterAgent
from config import Config

poster_blueprint = Blueprint("poster", __name__)


def _poster_dir() -> Path:
    path = Path(Config.POSTER_OUTPUT_PATH)
    path.mkdir(parents=True, exist_ok=True)
    return path


@poster_blueprint.get("/poster/<path:filename>")
def get_poster(filename: str):
    return send_from_directory(_poster_dir(), filename)


@poster_blueprint.post("/poster/generate")
def generate_poster():
    data = request.get_json(force=True) or {}
    username = data.get("username", "Champion")
    stats = data.get("stats")
    agent = PosterAgent(str(_poster_dir()))
    path = agent.create_poster(username, stats)
    filename = Path(path).name
    return jsonify({"filename": filename})
