import sys
import os
sys.path.append(os.path.dirname(__file__))

import logging
import threading
import locale
import atexit
import signal

from dotenv import load_dotenv
from web import create_app
from utils.env_helpers import get_env_str, get_env_bool, get_env_int
from init_db_core import init_db
from utils.github_service import fetch_repo_info
from fur_lang.i18n import t
from flask import Response, session
from dashboard.routes import dashboard
#app.register_blueprint(dashboard)

# --- Application-Factory: App-Objekt (für Gunicorn/Railway!) ---
app = create_app()
app.jinja_env.globals.update(t=t)
app.jinja_env.globals.update(current_lang=lambda: session.get("lang", "de"))

# 🌍 Locale setzen (UTF-8 empfohlen)
try:
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
except locale.Error:
    locale.setlocale(locale.LC_ALL, "")

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
        repo_data = fetch_repo_info()
        logging.info(f"✅ GitHub Repo geladen: {repo_data['full_name']}")
        logging.info(f"🔗 {repo_data['html_url']}")
    except Exception as e:
        log_error("GitHub", e)

def start_discord_bot():
    try:
        logging.info("🤖 Starte Discord-Bot...")
        from bot.bot_main import run_bot
        run_bot()
    except Exception as e:
        log_error("Discord-Bot", e)

def cleanup():
    logging.info("🔻 Anwendung wird beendet.")

def signal_handler(sig, frame):
    logging.info("🛑 SIGINT empfangen. Beende Anwendung...")
    cleanup()
    sys.exit(0)

if __name__ == "__main__":
    try:
        init_db()
        print("✅ Datenbank-Initialisierung erfolgreich.")
        atexit.register(cleanup)
        signal.signal(signal.SIGINT, signal_handler)
        check_github_repo()

        if get_env_bool("ENABLE_DISCORD_BOT", default=True):
            threading.Thread(target=start_discord_bot, daemon=True).start()

        port = get_env_int("PORT", required=False, default=8080)
        debug = True
        logging.info(f"🌐 Starte Webserver auf http://localhost:{port} (Debug={debug})")
        app.run(host="0.0.0.0", port=port, debug=debug)

    except KeyboardInterrupt:
        print("🛑 Manuell unterbrochen.")
    except Exception as e:
        log_error("Main", e)
        raise

@app.route("/health")
def healthcheck():
    return Response("ok", status=200)