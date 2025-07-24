from __future__ import annotations

import logging
from datetime import datetime, timedelta

import discord

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pymongo.collection import Collection

from config import Config
from mongo_service import get_collection

log = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="UTC")


def get_dm_image(dm_type: str) -> str:
    """Return configured DM image or fallback."""
    doc = get_collection("settings").find_one({"_id": f"dm_image_{dm_type}"})
    if doc and doc.get("value"):
        return doc["value"]
    return Config.DEFAULT_DM_IMAGE_URL


async def send_embed_dm(user, message: str, dm_type: str) -> None:
    """Send an embed DM with an optional image."""
    embed = discord.Embed(description=message)
    image_url = get_dm_image(dm_type) or Config.DEFAULT_DM_IMAGE_URL
    if image_url:
        embed.set_image(url=image_url)
    await user.send(embed=embed)


def get_dm_users() -> list[int]:
    """Return Discord user IDs that should receive DMs."""
    users: Collection = get_collection("users")
    return [int(u["discord_id"]) for u in users.find({"dm_enabled": True})]


async def send_dm(user, message: str) -> None:
    try:
        await user.send(message)
    except Exception as exc:  # noqa: BLE001
        log.error("DM to %s failed: %s", user, exc)


async def send_daily_dm(bot) -> None:
    today = datetime.utcnow().date().isoformat()
    flags = get_collection("flags")
    if flags.find_one({"_id": "daily_dm", "date": today}):
        return
    for uid in get_dm_users():
        user = await bot.fetch_user(uid)
        await send_embed_dm(user, "Good morning! Your events for today are ready.", "daily")
    flags.update_one({"_id": "daily_dm"}, {"$set": {"date": today}}, upsert=True)


async def check_upcoming_events(bot) -> None:
    now = datetime.utcnow()
    target = now + timedelta(minutes=10)
    events: Collection = get_collection("calendar_events")

    for event in events.find(
        {"start": {"$gte": now, "$lt": target}, "dm_warning_sent": {"$ne": True}}
    ):
        user_id = int(event.get("user_id", 0))
        if not user_id:
            continue
        user = await bot.fetch_user(user_id)
        await send_dm(user, f"\u23f0 Your event starts in 10 minutes: {event['title']}")
        events.update_one({"_id": event["_id"]}, {"$set": {"dm_warning_sent": True}})


def schedule_dm_tasks(bot) -> None:
    """Configure DM tasks with a midnight UTC trigger."""
    scheduler.add_job(
        send_daily_dm,
        trigger="cron",
        hour=0,
        minute=0,
        timezone="UTC",
        args=[bot],
    )
    scheduler.add_job(check_upcoming_events, "interval", minutes=1, args=[bot])
    scheduler.start()
