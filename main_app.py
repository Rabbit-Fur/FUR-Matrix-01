import atexit
import locale
import logging
import os
import signal
import sys
import threading
from dotenv import load_dotenv
# ➕ Healthcheck-Route für Railway
from flask import Response
from bot.bot_main import main as start_discord_bot, is_ready
from env_helpers import get_env_str, get_env_bool
from init_db_core import init_db
from github_api import fetch_repo_info
import bot
import web

# 🌍 Locale setzen
try:
    locale.setlocale(locale.LC_ALL, "")
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
except locale.Error:
    pass

# 📄 .env laden
load_dotenv()

# 📋 Logging konfigurieren
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def log_error(error_type, error):
    logging.error(f"{error_type}: {str(error)}", exc_info=True)

def check_github_repo():
    try:
        repo_data = fetch_repo_info("Rabbit-Fur", "System-by-FUR")
        logging.info(f"✅ GitHub Repo geladen: {repo_data['full_name']}")
        logging.info(f"🔗 {repo_data['html_url']}")
    except Exception as e:
        log_error("GitHub", e)

def start_bot():
    try:
        logging.info("🤖 Starte Discord-Bot...")
        bot.run_bot()
    except Exception as e:
        log_error("Bot", e)

def start_web():
    try:
        port = int(get_env_str("PORT", default="5000"))
        debug = get_env_str("FLASK_ENV", "production").lower() != "production"
        logging.info(f"🌐 Starte Webserver auf http://localhost:{port} (Debug={debug})")
        web.app.run(host="0.0.0.0", port=port, debug=debug)
    except Exception as e:
        log_error("Web", e)
        raise

def cleanup():
    logging.info("🔻 Anwendung wird beendet.")
    if hasattr(bot, "is_ready") and bot.is_ready():
        bot.close()
    web.app.config["SHUTTING_DOWN"] = True

def signal_handler(sig, frame):
    logging.info("🛑 SIGINT empfangen. Beende Anwendung...")
    if hasattr(bot, "is_ready") and bot.is_ready():
        bot.close()
    sys.exit(0)

if __name__ == "__main__":
    try:
        init_db()
        print("✅ Datenbank-Initialisierung erfolgreich.")
        atexit.register(cleanup)
        signal.signal(signal.SIGINT, signal_handler)
        check_github_repo()

        if get_env_bool("ENABLE_DISCORD_BOT", default=True):
            threading.Thread(target=start_bot, daemon=True).start()

        start_web()

    except KeyboardInterrupt:
        print("🛑 Manuell unterbrochen.")
    except Exception as e:
        log_error("Main", e)


@web.app.route("/health")
def healthcheck():
    return Response("ok", status=200)
