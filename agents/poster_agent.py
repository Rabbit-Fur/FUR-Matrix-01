"""PosterAgent generates simple champion posters using PIL."""

import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from config import Config


class PosterAgent:
    def __init__(self, output_dir: str | None = None):
        self.output_dir = Path(output_dir or Config.STATIC_FOLDER) / Config.CHAMPION_OUTPUT_REL_PATH
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_poster(self, username: str, stats: str | None = None) -> str:
        """Generate a poster image and return the file path."""
        file_path = self.output_dir / f"{uuid.uuid4().hex}.png"
        img = Image.new("RGB", (Config.IMG_WIDTH, Config.IMG_HEIGHT), Config.CHAMPION_BG_COLOR)
        draw = ImageDraw.Draw(img)
        try:
            font_title = ImageFont.truetype(Config.POSTER_FONT_TITLE_PATH, 64)
        except OSError:
            font_title = ImageFont.load_default()
        try:
            font_text = ImageFont.truetype(Config.POSTER_FONT_TEXT_PATH, 32)
        except OSError:
            font_text = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), username, font=font_title)
        x = (Config.IMG_WIDTH - (bbox[2] - bbox[0])) / 2
        y = (Config.IMG_HEIGHT - (bbox[3] - bbox[1])) / 3
        draw.text((x, y), username, font=font_title, fill=Config.CHAMPION_TEXT_COLOR)

        if stats:
            draw.text(
                (50, Config.IMG_HEIGHT - 100),
                stats,
                font=font_text,
                fill=Config.CHAMPION_SUBTEXT_COLOR,
            )

        img.save(file_path)
        return str(file_path)
