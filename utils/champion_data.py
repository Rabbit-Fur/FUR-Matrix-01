"""MongoDB-backed champion data helpers."""

from datetime import datetime
from typing import Dict, List, Optional

from database.mongo_client import db

hof = db["hall_of_fame"]


def save_champion_to_db(champion: Dict[str, str]) -> None:
    hof.insert_one(champion)


def load_champions_from_db() -> List[Dict[str, str]]:
    return list(hof.find().sort("created_at", 1))


def get_latest_champion() -> Optional[Dict[str, str]]:
    return hof.find_one(sort=[("created_at", -1)])


def add_champion(username: str, honor_title: str, month: str, poster_url: str) -> None:
    new_champ = {
        "username": username,
        "honor_title": honor_title,
        "month": month,
        "poster_url": poster_url,
        "created_at": datetime.utcnow(),
    }
    save_champion_to_db(new_champ)


def get_champion_by_month(month: str) -> Optional[Dict[str, str]]:
    return hof.find_one({"month": month})
