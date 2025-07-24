import os
from datetime import datetime

from config import Config
from utils.poster_generator import create_event_image, generate_event_poster


def test_generate_poster_daily_weekly(monkeypatch, tmp_path):
    monkeypatch.setattr(Config, "STATIC_FOLDER", str(tmp_path))
    monkeypatch.setattr(Config, "POSTER_OUTPUT_REL_PATH", "")

    event = {"title": "Test", "event_time": datetime(2025, 1, 1, 12, 0)}
    path_daily = generate_event_poster(event, "daily")
    assert os.path.isfile(path_daily)

    path_weekly = generate_event_poster(event, "weekly")
    assert os.path.isfile(path_weekly)


def test_create_event_image_bytes(monkeypatch):
    buf = create_event_image("Test", datetime(2025, 1, 1, 12, 0), "desc")
    assert isinstance(buf.getvalue(), (bytes, bytearray))
