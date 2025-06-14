"""Startpunkt f\u00fcr den Discord-Bot (FUR System)."""

import asyncio
import logging

try:
    import discord
    from discord.ext import commands
except ImportError:  # pragma: no cover - optional for testing
    import discord_util as discord  # type: ignore

    class commands:  # type: ignore
        class Bot(discord.Client):
            def command(self, *args, **kwargs):
                def wrapper(func):
                    return func

                return wrapper


import aiohttp

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Intents konfigurieren (f\u00fcr Member, Message Content, Guild Events etc.)
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Bot-Instanz wird erst bei Start erstellt
bot: commands.Bot | None = None


def is_ready() -> bool:
    """Return True if the bot reports readiness."""
    return bot is not None and bot.is_ready()


async def load_extensions(bot: commands.Bot) -> None:
    try:
        await bot.load_extension("bot.cogs.reminder_autopilot")
        await bot.load_extension("bot.cogs.reminder_optout")
        log.info("🔔 Reminder-Cogs geladen.")
    except Exception as e:  # pragma: no cover - optional for testing
        log.error("❌ Fehler beim Laden der Reminder-Cogs: %s", e)


async def run_bot(max_retries: int = 3) -> None:
    """Instantiate and start the bot asynchronously with retries."""
    from config import Config

    global bot
    connector = aiohttp.TCPConnector(resolver=aiohttp.AsyncResolver())
    bot = commands.Bot(command_prefix="!", intents=intents, connector=connector)

    @bot.event
    async def on_ready() -> None:
        log.info(
            "✅ Eingeloggt als %s (ID: %s)",
            bot.user,
            getattr(bot.user, "id", "n/a"),
        )

    await load_extensions(bot)

    for attempt in range(1, max_retries + 1):
        try:
            await bot.start(Config.DISCORD_TOKEN)
            return
        except aiohttp.ClientConnectorError as e:
            log.warning(
                "DNS-Fehler beim Verbinden zum Discord-Gateway (%s/%s): %s",
                attempt,
                max_retries,
                e,
            )
            if attempt == max_retries:
                log.critical(
                    "❌ Verbindung zum Discord-Gateway dauerhaft fehlgeschlagen.",
                    exc_info=True,
                )
                print(
                    "❌ Verbindung zum Discord-Gateway fehlgeschlagen. Bitte DNS/Netzwerk pr\u00fcfen."
                )
                raise
            await asyncio.sleep(5)
        except Exception as e:  # pragma: no cover - optional for testing
            log.critical("❌ Login fehlgeschlagen: %s", e, exc_info=True)
            raise


def main() -> None:
    """Entry point used by external scripts."""
    try:
        log.info("🚀 Discord-Bot wird gestartet...")
        asyncio.run(run_bot())
    except Exception as e:  # pragma: no cover - optional for testing
        log.critical("❌ Login fehlgeschlagen. %s", e, exc_info=True)


def run_bot_sync() -> None:
    """Backward compatible alias for :func:`main`."""
    main()
