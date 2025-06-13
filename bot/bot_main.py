
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
"""
bot_main.py – Startpunkt für den Discord-Bot (FUR System)
"""

import asyncio
import logging

"""
Unterstützt echten Betrieb (discord.py) und Fallback mit Stub für Testumgebungen.
Initialisiert Intents, registriert Events, startet den Bot.
"""

import logging

try:
    import discord
    from discord.ext import commands

    IS_STUB = False
except ImportError:
    # Fallback: Minimal-Stub nutzen, falls discord.py nicht installiert ist
    import discord_util as discord

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
    log.info(f"✅ Eingeloggt als {bot.user} (ID: {getattr(bot.user, 'id', 'n/a')})")


def is_ready() -> bool:
    return hasattr(bot, "is_ready") and bot.is_ready()


async def load_extensions(bot):
    try:
        await bot.load_extension("bot.cogs.reminder_autopilot")
        await bot.load_extension("bot.cogs.reminder_optout")
        log.info("🔔 Reminder-Cogs geladen.")
    except Exception as e:
        log.error(f"❌ Fehler beim Laden der Reminder-Cogs: {e}")


def main():
    try:
        from config import Config

        log.info("🚀 Discord-Bot wird gestartet...")

        async def start_bot():
            await load_extensions(bot)
            await bot.start(Config.DISCORD_TOKEN)

        asyncio.run(start_bot())

    except Exception as e:
        log.critical(
            f"❌ Login fehlgeschlagen. Prüfe Token und Intents: {e}", exc_info=True
        )


def run_bot():
    """Event: Bot ist bereit und eingeloggt."""
    log.info(f"✅ Eingeloggt als {bot.user} (ID: {getattr(bot.user, 'id', 'n/a')})")


def is_ready() -> bool:
    """
    Prüft, ob der Bot einsatzbereit ist.

    Returns:
        bool: True, wenn Bot bereit.
    """
    return hasattr(bot, "is_ready") and bot.is_ready()


def main() -> None:
    """
    Startet den Discord-Bot.

    Nutzt Token aus Config, meldet Fehler klar im Log.
    """
    try:
        from config import Config

        log.info("🚀 Discord-Bot wird gestartet...")
        bot.run(Config.DISCORD_TOKEN)
    except Exception as e:
        log.critical(
            f"❌ Login fehlgeschlagen. Prüfe Token und Intents: {e}", exc_info=True
        )


def run_bot() -> None:
    """
    Alias für Main (Kompatibilität zu anderem Systemcode).
    """
    main()
