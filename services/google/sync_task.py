"""Background task to sync Google Calendar periodically.

Example APScheduler setup::

    import asyncio
    from apscheduler.schedulers.background import BackgroundScheduler
    from services import CalendarService

    app = current_app
    scheduler = BackgroundScheduler()

    def sync_google():
        with app.app_context():
            service = CalendarService()
            asyncio.run(service.sync())

    scheduler.add_job(
        sync_google,
        "interval",
        minutes=current_app.config.get("GOOGLE_SYNC_INTERVAL_MINUTES", 30),
    )
    scheduler.start()

``GOOGLE_SYNC_INTERVAL_MINUTES`` controls the sync frequency in minutes.
OAuth tokens are loaded from ``GOOGLE_TOKEN_STORAGE_PATH`` or
``GOOGLE_CREDENTIALS_FILE``.
"""

from __future__ import annotations

import asyncio
import logging

from discord.ext import tasks
from flask import current_app

from .calendar_sync import sync_to_mongodb

log = logging.getLogger(__name__)


@tasks.loop(minutes=1)
async def google_sync_loop() -> None:
    """Run ``sync_to_mongodb`` in a thread within app context."""
    with current_app.app_context():
        await asyncio.to_thread(sync_to_mongodb)


def start_google_sync(interval_minutes: int | None = None) -> None:
    """Start the background sync loop with the given interval."""
    minutes = interval_minutes or current_app.config.get("GOOGLE_SYNC_INTERVAL_MINUTES", 30)
    if google_sync_loop.is_running():
        google_sync_loop.change_interval(minutes=minutes)
    else:
        google_sync_loop.change_interval(minutes=minutes)
        try:
            asyncio.get_running_loop()
            google_sync_loop.start()
        except RuntimeError:
            asyncio.run(google_sync_loop.coro())
    log.info("Google sync loop started (%s min)", minutes)
