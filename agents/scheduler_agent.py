"""
SchedulerAgent – verwaltet geplante Aufgaben, CRON-artige Abläufe, Reminder
"""

import logging
import time

import schedule

from champion.autopilot import run_champion_autopilot
from config import Config
from utils.google_sync import sync_google_calendar


class SchedulerAgent:
    def __init__(self):
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

    def schedule_google_sync(self, interval_minutes: int | None = None) -> None:
        """Schedule regular Google Calendar synchronization."""

        interval = interval_minutes or Config.GOOGLE_SYNC_INTERVAL_MINUTES
        job = schedule.every(interval).minutes.do(sync_google_calendar)
        self.jobs.append(job)
        logging.info(
            "\U0001f4c5 Google Calendar sync every %s minutes scheduled",
            interval,
        )
