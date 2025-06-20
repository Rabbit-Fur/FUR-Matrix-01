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

    async def send_discord_message(channel_id: int, content: str, file_path: str = None):
        """Sendet eine Nachricht über den echten Discord-Bot."""
        channel = bot.get_channel(channel_id)
        if channel is None:
            logging.warning(f"⚠️ Channel {channel_id} nicht gefunden.")
            return

        if file_path:
            file = discord.File(file_path)
            await channel.send(content, file=file)
        else:
            await channel.send(content)

else:
    # 📨 Fallback-Modus: Webhook-Poster
    import requests

    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

    def send_discord_message(channel_id: int, content: str, file_path: str = None):
        """Sendet eine Nachricht via Discord Webhook (ohne Bot)."""
        data = {"content": content}
        files = None

        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f)}
                response = requests.post(DISCORD_WEBHOOK_URL, data=data, files=files)
        else:
            response = requests.post(DISCORD_WEBHOOK_URL, json=data)

        if response.status_code not in [200, 204]:
            logging.error(f"❌ Webhook fehlgeschlagen: {response.status_code} – {response.text}")
        else:
            logging.info("✅ Webhook erfolgreich gesendet.")

    # Dummy für Kompatibilität
    bot = None


def require_roles(roles):
    """Decorator to enforce Discord role based access."""

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user_roles = session.get("discord_roles", [])
            if not any(role in user_roles for role in roles):
                return redirect(url_for("public.login"))
            return f(*args, **kwargs)

        return wrapped

    return decorator
