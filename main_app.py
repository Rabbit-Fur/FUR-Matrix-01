"""
main_app.py – Einstiegspunkt für das FUR-System (Web & Discord-Bot)
Mit Debug-Modus für lokale Entwicklung und sauberem Application-Factory-Pattern.
"""

import asyncio
import atexit
import locale
import logging
import signal
import sys
import threading

from dotenv import load_dotenv
from flask import Response, session
from werkzeug.middleware.proxy_fix import ProxyFix

# ✅ Korrekt: Agenten-Loader importieren
from agents.agenten_loader import init_agents  # noqa: E402
from agents.scheduler_agent import SchedulerAgent  # noqa: E402
from config import Config  # noqa: E402

# 🌍 Module
from database import close_db  # noqa: E402
from fur_lang.i18n import t  # noqa: E402
from init_db_core import init_db  # noqa: E402
from mongo_service import db  # MongoDB-Instanz  # noqa: E402
from utils.env_helpers import get_env_bool, get_env_int  # noqa: E402
from utils.github_service import fetch_repo_info  # noqa: E402
from web import create_app  # noqa: E402

# Call to create the Flask application instance via factory pattern
app = create_app()
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.teardown_appcontext(close_db)
app.jinja_env.globals.update(t=t)
app.jinja_env.globals.update(current_lang=lambda: session.get("lang", "de"))

# 🌍 Locale setzen
try:
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
except locale.Error:
    locale.setlocale(locale.LC_ALL, "")  # Fallback

# 📄 .env laden
load_dotenv()

# 📋 Logging konfigurieren
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def log_error(error_type, error):
    """Log an error with its type and exception details.

    Args:
        error_type: A short string describing the error category.
        error: The exception instance to log.

    Returns:
        None
    """
    logging.error(f"{error_type}: {str(error)}", exc_info=True)


def check_github_repo():
    """Fetch basic GitHub repository information and log it.

    Returns:
        None
    """
    try:
        repo_data = fetch_repo_info()
        logging.info(f"✅ GitHub Repo geladen: {repo_data['full_name']}")
        logging.info(f"🔗 {repo_data['html_url']}")
    except Exception as e:
        log_error("GitHub", e)


def start_discord_bot():
    """Start the Discord bot using an asyncio event loop.

    Returns:
        None
    """
    try:
        logging.info("🤖 Starte Discord-Bot...")
        from bot.bot_main import run_bot

        asyncio.run(run_bot())
    except Exception as e:
        log_error("Discord-Bot", e)


def cleanup():
    """Perform application cleanup when shutting down.

    Returns:
        None
    """
    logging.info("🔻 Anwendung wird beendet.")


def signal_handler(sig, frame):
    """Handle interrupt signals and exit gracefully.

    Args:
        sig: The received signal number.
        frame: The current stack frame when the signal was received.

    Returns:
        None
    """
    logging.info("🛑 SIGINT empfangen. Beende Anwendung...")
    cleanup()
    sys.exit(0)


# === Einstiegspunkt für lokale Ausführung ===
if __name__ == "__main__":
    try:
        init_db()
        logging.info("✅ Datenbank-Initialisierung erfolgreich.")

        # 🧠 Agenten laden (Reminder, Translation, Champion etc.)
        agents = init_agents(db=db, session=session)

        scheduler = SchedulerAgent()
        if Config.GOOGLE_CALENDAR_ID:
            scheduler.schedule_google_sync()
        if Config.DISCORD_WEBHOOK_URL:
            scheduler.schedule_champion_autopilot()
        threading.Thread(target=scheduler.run, daemon=True).start()

        atexit.register(cleanup)
        signal.signal(signal.SIGINT, signal_handler)
        check_github_repo()

        if get_env_bool("ENABLE_DISCORD_BOT", default=True):
            threading.Thread(target=start_discord_bot, daemon=True).start()

        port = get_env_int("PORT", default=8080)
        debug = get_env_bool("DEBUG", default=False)

        logging.info(f"🌐 Starte Webserver auf http://0.0.0.0:{port} (Debug={debug})")
        app.run(host="0.0.0.0", port=port, debug=debug)

    except KeyboardInterrupt:
        logging.info("🛑 Manuell unterbrochen.")
    except Exception as e:
        log_error("Main", e)
        raise


# ➕ Healthcheck für Railway/CI/Monitoring
@app.route("/health")
def healthcheck():
    """Return an HTTP 200 response to indicate application health.

    Returns:
        flask.Response: A simple "ok" response with status code 200.
    """
    return Response("ok", status=200)
