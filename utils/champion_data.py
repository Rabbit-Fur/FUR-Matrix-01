"""MongoDB-backed champion data helpers."""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from PIL import Image, ImageDraw, ImageFont

from config import Config
from mongo_service import get_collection

hof = get_collection("hall_of_fame")


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


def generate_champion_poster(username: str = "Champion") -> str:
    """Generate a simple champion poster image and return file path."""

    output_dir = os.path.join(Config.STATIC_FOLDER, Config.CHAMPION_OUTPUT_REL_PATH)
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{uuid.uuid4().hex}.png")

    img = Image.new("RGB", (Config.IMG_WIDTH, Config.IMG_HEIGHT), Config.CHAMPION_BG_COLOR)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(Config.POSTER_FONT_TITLE_PATH, 64)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), username, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (Config.IMG_WIDTH - text_width) / 2
    y = (Config.IMG_HEIGHT - text_height) / 2
    draw.text((x, y), username, font=font, fill=Config.CHAMPION_TEXT_COLOR)
    img.save(file_path)
    return file_path
