"""
discord_util.py – Discord-Integrationsmodul für Live-Betrieb und Webhook-Fallback

Entscheidet automatisch, ob ein echter discord.py-Bot oder nur Webhook-Kommunikation verwendet wird.
"""

import logging
import os
from functools import wraps

from flask import redirect, session, url_for

ENABLE_BOT = os.getenv("ENABLE_DISCORD_BOT", "false").lower() == "true"

if ENABLE_BOT:
    # ✅ Echtbetrieb: discord.py
    import discord
    from discord.ext import commands

    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix="!", intents=intents)

    async def send_discord_message(
        channel_id: int, content: str, image_url: str | None = None
    ) -> None:
        """Sendet eine Nachricht über den echten Discord-Bot."""
        channel = bot.get_channel(channel_id)
        if channel is None:
            logging.warning(f"⚠️ Channel {channel_id} nicht gefunden.")
            return

        if image_url:
            embed = discord.Embed()
            embed.set_image(url=image_url)
            await channel.send(content, embed=embed)
        else:
            await channel.send(content)

else:
    # 📨 Fallback-Modus: Webhook-Poster
    import requests

    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

    def send_discord_message(channel_id: int, content: str, image_url: str | None = None) -> bool:
        """Sendet eine Nachricht via Discord Webhook (ohne Bot)."""
        if not DISCORD_WEBHOOK_URL:
            logging.warning(
                "⚠️ DISCORD_WEBHOOK_URL fehlt – Fallback-Benachrichtigung wird übersprungen."
            )
            return False

        data = {"content": content}
        if image_url:
            data["embeds"] = [{"image": {"url": image_url}}]

        response = requests.post(DISCORD_WEBHOOK_URL, json=data)

        if response.status_code not in [200, 204]:
            logging.error(f"❌ Webhook fehlgeschlagen: {response.status_code} – {response.text}")
            return False

        logging.info("✅ Webhook erfolgreich gesendet.")
        return True

    # Dummy für Kompatibilität
    bot = None


def require_roles(roles):
    """Decorator to enforce Discord role based access."""

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user_roles = session.get("discord_roles", [])
            if not any(role in user_roles for role in roles):
                return redirect(url_for("auth.login"))
            return f(*args, **kwargs)

        return wrapped

    return decorator
