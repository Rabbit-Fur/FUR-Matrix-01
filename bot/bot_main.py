"""
bot_main.py – Startpunkt für den Discord-Bot im FUR-System.

Unterstützt echten Discord.py-Bot oder Stub/Webhook-Modus je nach ENV.
"""

import asyncio
import logging
import os
import aiohttp

from config import Config

# 🧠 Umschalten zwischen echtem Bot & Stub
USE_DISCORD_BOT = os.getenv("ENABLE_DISCORD_BOT", "false").lower() == "true"

if USE_DISCORD_BOT:
    import discord
    from discord.ext import commands
else:
    import discord_util as discord
    from discord_util import Client as BotStub

    class commands:  # type: ignore
        Bot = BotStub

# 🔧 Logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ✅ Intents konfigurieren
intents = discord.Intents.all()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = None  # Global Bot-Objekt (commands.Bot oder Stub)


def create_bot() -> commands.Bot:
    """Initialisiert eine Bot-Instanz (echter Bot oder Stub)."""
    connector = aiohttp.TCPConnector(resolver=aiohttp.AsyncResolver())

    if USE_DISCORD_BOT:
        new_bot = commands.Bot(command_prefix="!", intents=intents, connector=connector)

        @new_bot.event
        async def on_ready():
            log.info("✅ Eingeloggt als %s (ID: %s)", new_bot.user, getattr(new_bot.user, "id", "n/a"))

    else:
        new_bot = BotStub()
        log.info("🧪 Stub-Bot aktiv (kein Gateway, nur Simulation)")

    return new_bot


async def load_extensions(bot_instance: commands.Bot):
    """Lädt alle aktiven Cogs (z. B. Reminder-System)."""
    try:
        await bot_instance.load_extension("bot.cogs.reminder_autopilot")
        await bot_instance.load_extension("bot.cogs.reminder_optout")
        log.info("🔔 Reminder-Cogs erfolgreich geladen.")
    except Exception as e:
        log.error("❌ Fehler beim Laden der Cogs: %s", e)


async def run_bot(max_retries: int = 3) -> None:
    """Startet den Discord-Bot mit optionalem Retry bei Verbindungsfehlern."""
    global bot
    bot = create_bot()

    if USE_DISCORD_BOT:
        await load_extensions(bot)

        for attempt in range(1, max_retries + 1):
            try:
                await bot.start(Config.DISCORD_TOKEN)
                return
            except aiohttp.ClientConnectorError as e:
                log.warning("DNS-Verbindungsfehler (%s/%s): %s", attempt, max_retries, e)
                if attempt == max_retries:
                    log.critical("❌ Discord-Gateway dauerhaft unerreichbar.", exc_info=True)
                    raise
                await asyncio.sleep(5)
            except Exception as e:
                log.critical("❌ Bot-Start fehlgeschlagen: %s", e, exc_info=True)
                raise
    else:
        # Simulierter Bot (kein Gateway)
        bot.run("FAKE_TOKEN")  # ersetzt echten Startaufruf für Tests


def is_ready() -> bool:
    """Status-Check: Ist Bot einsatzbereit?"""
    return bot is not None and getattr(bot, "is_ready", lambda: False)()


def main() -> None:
    """Synchroner Entry-Point."""
    try:
        log.info("🚀 Discord-Bot wird gestartet...")
        asyncio.run(run_bot())
    except Exception as e:
        log.critical("❌ Bot konnte nicht gestartet werden: %s", e, exc_info=True)


def run_bot_sync() -> None:
    """Kompatibilitäts-Alias für `main()`."""
    main()
