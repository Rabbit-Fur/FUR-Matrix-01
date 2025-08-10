"""Background task to sync Google Calendar periodically."""

from __future__ import annotations

import asyncio
import logging

from discord.ext import tasks
from flask import current_app

from .calendar_sync import SyncTokenExpired, sync_to_mongodb

log = logging.getLogger(__name__)


@tasks.loop(minutes=1)
async def google_sync_loop(app) -> None:
    """Run ``sync_to_mongodb`` in a thread within app context."""
    with app.app_context():
        try:
            await asyncio.to_thread(sync_to_mongodb)
        except SyncTokenExpired:
            log.warning("Google credentials missing – skipping sync")


def start_google_sync(interval_minutes: int | None = None) -> None:
    """Start the background sync loop with the given interval."""
    app = current_app._get_current_object()
    default = current_app.config.get("GOOGLE_SYNC_INTERVAL_MINUTES", 30)
    minutes = interval_minutes or default
    if google_sync_loop.is_running():
        google_sync_loop.change_interval(minutes=minutes)
    else:
        google_sync_loop.start(app)
        if minutes != 1:
            google_sync_loop.change_interval(minutes=minutes)
    log.info("Google sync loop started (%s min)", minutes)
