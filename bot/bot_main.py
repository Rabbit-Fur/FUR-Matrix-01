"""Startpunkt für den Discord-Bot (FUR System)."""

import asyncio
import logging

"""Unterstützt echten Betrieb (discord.py) und Fallback mit Stub."""

try:
    import discord
    from discord.ext import commands

    IS_STUB = False
except ImportError:  # pragma: no cover - optional for testing
    import discord_util as discord  # type: ignore

    IS_STUB = True

    class commands:
        class Bot(discord.Client):
            def command(self, *args, **kwargs):
                def wrapper(func):
                    return func

                return wrapper


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Intents konfigurieren (für Member, Message Content, Guild Events etc.)
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Bot-Instanz erstellen
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    log.info(
        "✅ Eingeloggt als %s (ID: %s)",
        bot.user,
        getattr(bot.user, "id", "n/a"),
    )


def is_ready() -> bool:
    """Return True if the bot reports readiness."""
    return hasattr(bot, "is_ready") and bot.is_ready()


async def load_extensions(bot):
    try:
        await bot.load_extension("bot.cogs.reminder_autopilot")
        await bot.load_extension("bot.cogs.reminder_optout")
        log.info("🔔 Reminder-Cogs geladen.")
    except Exception as e:
        log.error(f"❌ Fehler beim Laden der Reminder-Cogs: {e}")


async def start_bot() -> None:
    """Load cogs and start the bot asynchronously."""
    from config import Config

    await load_extensions(bot)
    await bot.start(Config.DISCORD_TOKEN)


def main() -> None:
    """Entry point used by external scripts."""
    try:
        log.info("🚀 Discord-Bot wird gestartet...")
        asyncio.run(start_bot())
    except Exception as e:
        log.critical(
            "❌ Login fehlgeschlagen. Prüfe Token und Intents: %s", e, exc_info=True
        )


def run_bot() -> None:
    """Backward compatible alias for :func:`main`."""
    main()
