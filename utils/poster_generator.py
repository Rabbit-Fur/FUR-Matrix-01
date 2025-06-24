from __future__ import annotations

import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from config import Config

DEFAULT_BG_COLOR = Config.CHAMPION_BG_COLOR
TITLE_COLOR = Config.CHAMPION_TEXT_COLOR
TEXT_COLOR = Config.CHAMPION_SUBTEXT_COLOR


def generate_poster(title: str, lines: list[str], output_dir: str | None = None) -> str:
    """Create a simple poster image with a title and lines of text."""
    out_dir = Path(output_dir or Config.STATIC_FOLDER) / Config.POSTER_OUTPUT_REL_PATH
    out_dir.mkdir(parents=True, exist_ok=True)

    file_path = out_dir / f"{uuid.uuid4().hex}.png"

    img = Image.new("RGB", (Config.IMG_WIDTH, Config.IMG_HEIGHT), DEFAULT_BG_COLOR)
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype(Config.POSTER_FONT_TITLE_PATH, 64)
    except OSError:
        font_title = ImageFont.load_default()
    try:
        font_text = ImageFont.truetype(Config.POSTER_FONT_TEXT_PATH, 32)
    except OSError:
        font_text = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), title, font=font_title)
    x = (Config.IMG_WIDTH - (bbox[2] - bbox[0])) / 2
    y = 60
    draw.text((x, y), title, font=font_title, fill=TITLE_COLOR)

    y += bbox[3] - bbox[1] + 40
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_text)
        x = (Config.IMG_WIDTH - (bbox[2] - bbox[0])) / 2
        draw.text((x, y), line, font=font_text, fill=TEXT_COLOR)
        y += bbox[3] - bbox[1] + 10

    img.save(file_path)
    return str(file_path)
