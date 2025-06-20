from datetime import datetime, timedelta

from agents.webhook_agent import WebhookAgent
from config import Config
from dashboard.weekly_log_generator import generate_markdown_report
from mongo_service import get_collection


def post_report() -> bool:
    """Compile the weekly markdown report and post it via ``WebhookAgent``."""
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
    markdown_path = generate_markdown_report(participation, upcoming, filename)
    with open(markdown_path, "r", encoding="utf-8") as fh:
        content = f"```\n{fh.read()}\n```"

    webhook = WebhookAgent(Config.DISCORD_WEBHOOK_URL)
    return webhook.send(content=content)
