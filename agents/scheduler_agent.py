"""
SchedulerAgent – verwaltet geplante Aufgaben, CRON-artige Abläufe, Reminder
"""

import logging
import time
from datetime import datetime

import schedule

from champion.autopilot import run_champion_autopilot
from mongo_service import get_collection
from utils import champion_data
from services.google.sync_task import start_google_sync


class SchedulerAgent:
    def __init__(self, app, mongo_db):
        self.app = app
        self.mongo_db = mongo_db
        self.jobs = []

    def schedule_job(self, func, interval=60):
        job = schedule.every(interval).seconds.do(func)
        self.jobs.append(job)
        logging.info(f"📆 Geplanter Task alle {interval} Sekunden gestartet")

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def schedule_champion_autopilot(
        self, interval_hours: int = 24, month: str | None = None, username: str | None = None
    ) -> None:
        """Schedule the champion autopilot to run regularly."""

        job = schedule.every(interval_hours).hours.do(
            run_champion_autopilot, month=month, username=username
        )
        self.jobs.append(job)
        logging.info("\U0001f4c5 Champion Autopilot every %s hours scheduled", interval_hours)

    def schedule_monthly_champion_job(self) -> None:
        """Schedule monthly champion determination and announcement."""

        def monthly_job() -> None:
            try:
                collection = get_collection("leaderboard")
                top = list(collection.find().sort("score", -1).limit(1))
                if not top:
                    logging.info("No leaderboard data for monthly champion")
                    return
                username = top[0].get("username", "Champion")
                month = datetime.utcnow().strftime("%Y-%m")
                poster_path = champion_data.generate_champion_poster(username)
                champion_data.add_champion(username, "Monthly Champion", month, poster_path)
                run_champion_autopilot(month=month, username=username)
            except Exception:  # noqa: BLE001 - log exception only
                logging.exception("Monthly champion job failed")

        job = schedule.every(30).days.do(monthly_job)
        self.jobs.append(job)
        logging.info("\U0001f4c5 Monthly champion job scheduled")

    def schedule_google_sync(self, interval_minutes: int | None = None) -> None:
        """Schedule regular Google Calendar synchronization."""
        minutes = interval_minutes or self.app.config.get("GOOGLE_SYNC_INTERVAL_MINUTES", 2)
        start_google_sync(self.app, self.mongo_db)
        logging.info(
            "\U0001f4c5 Google Calendar sync every %s minutes scheduled via loop",
            minutes,
        )
