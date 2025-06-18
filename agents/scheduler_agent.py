"""
SchedulerAgent – verwaltet geplante Aufgaben, CRON-artige Abläufe, Reminder
"""

import logging
import schedule
import time

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
