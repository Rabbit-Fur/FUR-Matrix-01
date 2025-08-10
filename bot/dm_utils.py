from __future__ import annotations

import discord
from config import Config
from mongo_service import get_collection
from urllib.parse import urljoin


def _ensure_url(path: str) -> str:
    """Prepend ``Config.BASE_URL`` if ``path`` is relative."""
    if path and not path.startswith("http"):
        return urljoin(Config.BASE_URL, path.lstrip("/"))
    return path


def get_dm_image(dm_type: str) -> str:
    """Return configured DM image or fallback."""
    doc = get_collection("settings").find_one({"_id": f"dm_image_{dm_type}"})
    if doc and doc.get("value"):
        return _ensure_url(doc["value"])
    return _ensure_url(Config.DEFAULT_DM_IMAGE_URL)


def get_dm_users() -> list[int]:
    """Return Discord user IDs that should receive DMs."""
    users = get_collection("users")
    return [int(u["discord_id"]) for u in users.find({"dm_enabled": True})]


async def send_embed_dm(user, message: str, dm_type: str) -> None:
    """Send an embed DM with an optional image."""
    embed = discord.Embed(description=message)
    image_url = get_dm_image(dm_type) or Config.DEFAULT_DM_IMAGE_URL
    if image_url:
        embed.set_image(url=image_url)
    await user.send(embed=embed)


__all__ = ["get_dm_image", "get_dm_users", "send_embed_dm"]
