"""
bot_main.py – Startpunkt für den Discord-Bot (FUR System)

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
                def wrapper(func): return func
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
    main()
