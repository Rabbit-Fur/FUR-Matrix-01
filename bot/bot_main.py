"""
bot_main.py – Startpunkt für den Discord-Bot (FUR System)
"""

import logging
import asyncio

try:
    import discord
    from discord.ext import commands
    IS_STUB = False
except ImportError:
    import discord_util as discord
    IS_STUB = True

    class commands:
        class Bot(discord.Client):
            def command(self, *args, **kwargs):
                def wrapper(func): return func
                return wrapper

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
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
    main()
