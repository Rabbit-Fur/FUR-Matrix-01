import os
from datetime import datetime, timedelta

import logging
import requests

from mongo_service import get_collection

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
LOG_DIR = "core/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger(__name__)


def generate_markdown_report(participation, upcoming, filename):
    lines = [f"# 📊 Wöchentlicher Report – {datetime.utcnow().date()}\n"]

    lines.append("## 🏅 Top-Teilnehmer der Woche")
    for row in participation:
        lines.append(f"- `{row['user_id']}` – **{row['count']}x teilgenommen**")

    lines.append("\n## 🔮 Kommende Events")
    for ev in upcoming:
        lines.append(f"- {ev['title']} – {ev['event_time'].strftime('%d.%m.%Y %H:%M')} UTC")

    path = os.path.join(LOG_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def send_webhook(markdown_file):
    if not WEBHOOK_URL:
        return
    with open(markdown_file, "r", encoding="utf-8") as f:
        data = {"content": f"```\n{f.read()}\n```"}
    try:
        requests.post(WEBHOOK_URL, json=data, timeout=10)
    except Exception as e:
        logger.error("Webhook-Fehler: %s", e)


def run_weekly_log():
    now = datetime.utcnow()
    week_start = now - timedelta(days=7)
    week_end = now + timedelta(days=7)

    participation = list(
        get_collection("participants").aggregate(
            [
                {
                    "$lookup": {
                        "from": "events",
                        "localField": "event_id",
                        "foreignField": "_id",
                        "as": "event",
                    }
                },
                {"$unwind": "$event"},
                {"$match": {"event.event_time": {"$gte": week_start, "$lte": now}}},
                {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
            ]
        )
    )

    upcoming = list(
        get_collection("events")
        .find({"event_time": {"$gte": now, "$lte": week_end}}, {"title": 1, "event_time": 1})
        .sort("event_time", 1)
    )

    filename = f"{now.date()}-weekly.md"
    markdown = generate_markdown_report(participation, upcoming, filename)
    send_webhook(markdown)
    logger.info("Weekly log created: %s", filename)
