"""
bot_main.py – Startpunkt für den Discord-Bot (FUR System)
<<<<<<< HEAD
"""

import logging
import asyncio
=======

Unterstützt echten Betrieb (discord.py) und Fallback mit Stub für Testumgebungen.
Initialisiert Intents, registriert Events, startet den Bot.
"""

import logging
>>>>>>> b9da45a45805ab6a1f5377830ffb553178ced3ba

try:
    import discord
    from discord.ext import commands
    IS_STUB = False
except ImportError:
<<<<<<< HEAD
=======
    # Fallback: Minimal-Stub nutzen, falls discord.py nicht installiert ist
>>>>>>> b9da45a45805ab6a1f5377830ffb553178ced3ba
    import discord_util as discord
    IS_STUB = True

    class commands:
        class Bot(discord.Client):
            def command(self, *args, **kwargs):
                def wrapper(func): return func
                return wrapper

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

<<<<<<< HEAD
=======
# Intents konfigurieren (für Member, Message Content, Guild Events etc.)
>>>>>>> b9da45a45805ab6a1f5377830ffb553178ced3ba
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

<<<<<<< HEAD
=======
# Bot-Instanz erstellen
>>>>>>> b9da45a45805ab6a1f5377830ffb553178ced3ba
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
<<<<<<< HEAD
    log.info(f"✅ Eingeloggt als {bot.user} (ID: {getattr(bot.user, 'id', 'n/a')})")

def is_ready() -> bool:
    return hasattr(bot, "is_ready") and bot.is_ready()

async def load_extensions(bot):
    try:
        await bot.load_extension("bot.cogs.reminder_autopilot")
        log.info("🔔 Reminder-Autopilot geladen.")
    except Exception as e:
        log.error(f"❌ Fehler beim Laden des Reminder-Cogs: {e}")

def main():
    try:
        from config import Config
        log.info("🚀 Discord-Bot wird gestartet...")

        async def start_bot():
            await load_extensions(bot)
            await bot.start(Config.DISCORD_TOKEN)

        asyncio.run(start_bot())

    except Exception as e:
        log.critical(f"❌ Login fehlgeschlagen. Prüfe Token und Intents: {e}", exc_info=True)

def run_bot():
=======
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
        log.critical(f"❌ Login fehlgeschlagen. Prüfe Token und Intents: {e}", exc_info=True)

def run_bot() -> None:
    """
    Alias für Main (Kompatibilität zu anderem Systemcode).
    """
>>>>>>> b9da45a45805ab6a1f5377830ffb553178ced3ba
    main()
