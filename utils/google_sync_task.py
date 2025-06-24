"""Background task to sync Google Calendar periodically."""

from __future__ import annotations

import asyncio
import logging
import os

from discord.ext import tasks

from utils.google_sync import sync_google_calendar

log = logging.getLogger(__name__)

DEFAULT_INTERVAL_MINUTES = int(os.getenv("GOOGLE_SYNC_INTERVAL_MINUTES", "30"))


@tasks.loop(minutes=DEFAULT_INTERVAL_MINUTES)
async def google_sync_loop() -> None:
    """Run ``sync_google_calendar`` in a thread."""
    await asyncio.to_thread(sync_google_calendar)


def start_google_sync(interval_minutes: int | None = None) -> None:
    """Start the background sync loop with the given interval."""
    minutes = interval_minutes or DEFAULT_INTERVAL_MINUTES
    if google_sync_loop.is_running():
        google_sync_loop.change_interval(minutes=minutes)
    else:
        if minutes != DEFAULT_INTERVAL_MINUTES:
            google_sync_loop.change_interval(minutes=minutes)
        google_sync_loop.start()
    log.info("Google sync loop started (%s min)", minutes)
