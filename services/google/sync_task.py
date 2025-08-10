from __future__ import annotations

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from .calendar_sync import sync_to_mongodb

log = logging.getLogger(__name__)
_scheduler: BackgroundScheduler | None = None


def start_google_sync(app, mongo_db):
    """Start an interval job syncing Google Calendar to MongoDB."""
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()

    interval = int(app.config.get("GOOGLE_SYNC_INTERVAL_MINUTES", 2))

    def _job():
        with app.app_context():
            count = sync_to_mongodb(
                mongo_db=mongo_db,
                collection_name="calendar_events",
                max_results=250,
                time_min=datetime.now(timezone.utc),
            )
            log.info("Google Calendar sync finished (upserts/updates: %s)", count)

    _scheduler.add_job(
        _job,
        "interval",
        minutes=interval,
        id="google_calendar_sync",
        replace_existing=True,
    )

    if not _scheduler.running:
        _scheduler.start()
        log.info("Google sync loop started (every %s min)", interval)
