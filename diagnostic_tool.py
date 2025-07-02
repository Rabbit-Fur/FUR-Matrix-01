"""Utility to inspect events, channel mappings, poster files and logs."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Iterable
import logging

from config import Config
from utils import event_helpers


log = logging.getLogger(__name__)


def get_recent_events() -> str:
    """Return formatted events for today using :mod:`utils.event_helpers`."""
    events = event_helpers.get_events_for(datetime.utcnow())
    if not events:
        return "No events found."
    return event_helpers.format_events(events)


def get_channel_mapping() -> dict[str, int | str | None]:
    """Return a dict with relevant channel configuration values."""
    return {
        "REMINDER_CHANNEL_ID": Config.REMINDER_CHANNEL_ID,
        "DISCORD_EVENT_CHANNEL_ID": Config.DISCORD_EVENT_CHANNEL_ID,
        "EVENT_CHANNEL_ID": Config.EVENT_CHANNEL_ID,
        "EVENT_REMINDER_CHANNEL": Config.EVENT_REMINDER_CHANNEL,
        "CHAMPION_ANNOUNCEMENT_CHANNEL": Config.CHAMPION_ANNOUNCEMENT_CHANNEL,
    }


def get_poster_files() -> list[str]:
    """Return a list of generated poster file paths."""
    base = Path(Config.STATIC_FOLDER)
    candidates = [
        base / Config.POSTER_OUTPUT_REL_PATH,
        base / Config.CHAMPION_OUTPUT_REL_PATH,
        base / "generated",
    ]
    files: list[str] = []
    for directory in candidates:
        if directory.is_dir():
            files.extend(str(p) for p in directory.glob("*.png"))
    return files


def get_log_files(log_dir: str | Path = "core/logs") -> list[str]:
    """Return Markdown log files from *log_dir*."""
    path = Path(log_dir)
    if not path.is_dir():
        return []
    return [str(p) for p in sorted(path.glob("*.md"))]


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="FUR diagnostic utility")
    parser.add_argument("--events", action="store_true", help="Show recent events")
    parser.add_argument("--channels", action="store_true", help="Show channel mappings")
    parser.add_argument("--posters", action="store_true", help="List poster files")
    parser.add_argument("--logs", action="store_true", help="List log files")
    args = parser.parse_args(args=argv)

    if not any(vars(args).values()):
        parser.print_help()
        return

    if args.events:
        log.info("== Recent Events ==")
        log.info(get_recent_events())
    if args.channels:
        log.info("== Channel Mappings ==")
        for key, value in get_channel_mapping().items():
            log.info("%s: %s", key, value)
    if args.posters:
        log.info("== Poster Files ==")
        for item in get_poster_files():
            log.info(item)
    if args.logs:
        log.info("== Log Files ==")
        for item in get_log_files():
            log.info(item)


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()
