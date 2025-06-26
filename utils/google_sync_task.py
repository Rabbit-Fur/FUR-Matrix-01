"""Background task to sync Google Calendar periodically."""

from __future__ import annotations

import asyncio
import logging
import os

from discord.ext import tasks
from flask import current_app

from utils.google_sync import sync_google_calendar
from web import create_app

log = logging.getLogger(__name__)

DEFAULT_INTERVAL_MINUTES = int(os.getenv("GOOGLE_SYNC_INTERVAL_MINUTES", "30"))


_app = None


def _get_app():
    """Return a Flask application instance."""
    global _app
    try:
        return current_app._get_current_object()
    except RuntimeError:
        if _app is None:
            _app = create_app()
        return _app


@tasks.loop(minutes=DEFAULT_INTERVAL_MINUTES)
async def google_sync_loop() -> None:
    """Run ``sync_google_calendar`` in a thread within app context."""
    app = _get_app()
    with app.app_context():
        await asyncio.to_thread(sync_google_calendar)


def start_google_sync(interval_minutes: int | None = None) -> None:
    """Start the background sync loop with the given interval."""
    minutes = interval_minutes or DEFAULT_INTERVAL_MINUTES
    if google_sync_loop.is_running():
        google_sync_loop.change_interval(minutes=minutes)
    else:
        if minutes != DEFAULT_INTERVAL_MINUTES:
            google_sync_loop.change_interval(minutes=minutes)
        try:
            asyncio.get_running_loop()
            google_sync_loop.start()
        except RuntimeError:
            asyncio.run(google_sync_loop.coro())
    log.info("Google sync loop started (%s min)", minutes)
