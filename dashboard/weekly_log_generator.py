import os
from datetime import datetime, timedelta

import requests

from database.mongo_client import db

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
LOG_DIR = "core/logs"
os.makedirs(LOG_DIR, exist_ok=True)


def generate_markdown_report(participation, upcoming, filename):
    lines = [f"# 📊 Wöchentlicher Report – {datetime.utcnow().date()}\n"]

    lines.append("## 🏅 Top-Teilnehmer der Woche")
    for row in participation:
        lines.append(f"- `{row['user_id']}` – **{row['count']}x teilgenommen**")

    lines.append("\n## 🔮 Kommende Events")
    for event in upcoming:
        lines.append(f"- **{event['title']}** – `{event['event_time']}`")

    lines.append("\n[Zum Admin-Report im Web](/admin/weekly-report)")
    content = "\n".join(lines)

    with open(os.path.join(LOG_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content)

    return content


def send_webhook(content):
    if not WEBHOOK_URL:
        print("⚠️ Kein DISCORD_WEBHOOK_URL gesetzt.")
        return
    try:
        requests.post(WEBHOOK_URL, json={"content": content[:1900]})
    except Exception as e:
        print(f"❌ Webhook-Fehler: {e}")


def run_weekly_log():
    now = datetime.utcnow()
    week_start = now - timedelta(days=7)
    week_end = now + timedelta(days=7)

    participation = list(
        db["participants"].aggregate(
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
        db["events"]
        .find(
            {"event_time": {"$gte": now, "$lte": week_end}},
            {"title": 1, "event_time": 1},
        )
        .sort("event_time", 1)
    )

    filename = f"{now.date()}-weekly.md"
    markdown = generate_markdown_report(participation, upcoming, filename)
    send_webhook(markdown)
    print(f"✅ Weekly log created: {filename}")


if __name__ == "__main__":
    run_weekly_log()
