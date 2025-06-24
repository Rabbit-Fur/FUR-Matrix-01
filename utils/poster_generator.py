"""Poster generation utilities for events."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from config import Config

# Background images for each mode (using default static directory)
MODE_BACKGROUNDS = {
    "daily": Path(Config.STATIC_FOLDER) / "img" / "background.jpg",
    "weekly": Path(Config.STATIC_FOLDER) / "img" / "background2.jpg",
}


def _load_font(path: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Return truetype font or default fallback."""
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def generate_poster(event: dict, mode: str = "daily") -> str:
    """Generate a poster image for an event.

    Parameters
    ----------
    event: dict
        Event information (expects ``title`` and ``event_time``).
    mode: str
        ``daily`` or ``weekly``.

    Returns
    -------
    str
        Path to the created image file.
    """
    if mode not in MODE_BACKGROUNDS:
        raise ValueError("mode must be 'daily' or 'weekly'")

    output_dir = Path(Config.STATIC_FOLDER) / Config.POSTER_OUTPUT_REL_PATH
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"{uuid.uuid4().hex}.png"

    bg_path = MODE_BACKGROUNDS.get(mode, Path(Config.POSTER_BG_DEFAULT_PATH))
    if not bg_path.is_file():
        bg_path = Path(Config.POSTER_BG_DEFAULT_PATH)

    img = Image.open(bg_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    title_font = _load_font(Config.POSTER_FONT_TITLE_PATH, 64)
    text_font = _load_font(Config.POSTER_FONT_TEXT_PATH, 32)

    title = event.get("title", "Event")
    dt = event.get("event_time")
    if isinstance(dt, datetime):
        dt_text = dt.strftime("%d.%m.%Y %H:%M UTC")
    else:
        dt_text = str(dt) if dt else ""

    width, height = img.size
    bbox = draw.textbbox((0, 0), title, font=title_font)
    x = (width - (bbox[2] - bbox[0])) / 2
    y = height / 3
    draw.text((x, y), title, font=title_font, fill=Config.TEXT_COLOR)

    if dt_text:
        bbox2 = draw.textbbox((0, 0), dt_text, font=text_font)
        x2 = (width - (bbox2[2] - bbox2[0])) / 2
        draw.text((x2, y + 80), dt_text, font=text_font, fill=Config.TEXT_COLOR)

    img.save(file_path)
    return str(file_path)
