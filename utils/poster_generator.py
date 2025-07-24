from __future__ import annotations

"""Poster generation utilities for events."""

import uuid
from datetime import datetime
from io import BytesIO
from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont

from config import Config

DEFAULT_BG_COLOR = Config.CHAMPION_BG_COLOR
TITLE_COLOR = Config.CHAMPION_TEXT_COLOR
TEXT_COLOR = Config.CHAMPION_SUBTEXT_COLOR


def generate_text_poster(title: str, lines: list[str], output_dir: str | None = None) -> str:
    """Create a simple poster image with a title and multiple lines of text."""
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


def generate_event_poster(event: dict, mode: str = "daily") -> str:
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


def create_event_image(title: str, date: datetime | None, description: str | None) -> BytesIO:
    """Return an event poster image as ``BytesIO`` buffer."""
    bg_path = Path(Config.POSTER_BG_DEFAULT_PATH)
    if bg_path.is_file():
        img = Image.open(bg_path).convert("RGB")
        img = img.resize((Config.IMG_WIDTH, Config.IMG_HEIGHT))
    else:
        img = Image.new("RGB", (Config.IMG_WIDTH, Config.IMG_HEIGHT), DEFAULT_BG_COLOR)

    draw = ImageDraw.Draw(img)
    title_font = _load_font(Config.POSTER_FONT_TITLE_PATH, 60)
    text_font = _load_font(Config.POSTER_FONT_TEXT_PATH, 32)

    y = 80
    bbox = draw.textbbox((0, 0), title, font=title_font)
    x = (Config.IMG_WIDTH - (bbox[2] - bbox[0])) / 2
    draw.text((x, y), title, font=title_font, fill=TITLE_COLOR)
    y += bbox[3] - bbox[1] + 30

    if isinstance(date, datetime):
        dt_text = date.strftime("%d.%m.%Y %H:%M UTC")
    else:
        dt_text = str(date) if date else ""
    if dt_text:
        bbox = draw.textbbox((0, 0), dt_text, font=text_font)
        x = (Config.IMG_WIDTH - (bbox[2] - bbox[0])) / 2
        draw.text((x, y), dt_text, font=text_font, fill=TEXT_COLOR)
        y += bbox[3] - bbox[1] + 20

    if description:
        for line in textwrap.wrap(description, width=40)[:5]:
            bbox = draw.textbbox((0, 0), line, font=text_font)
            x = (Config.IMG_WIDTH - (bbox[2] - bbox[0])) / 2
            draw.text((x, y), line, font=text_font, fill=TEXT_COLOR)
            y += bbox[3] - bbox[1] + 5

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
