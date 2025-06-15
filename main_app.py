"""
main_app.py – Einstiegspunkt für das FUR-System (Web & Discord-Bot)
Mit Debug-Modus für lokale Entwicklung und sauberem Application-Factory-Pattern.
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))

import asyncio
import atexit
import locale
import logging
import signal
import threading

from dotenv import load_dotenv
from flask import Response, session

from dashboard.routes import dashboard
from fur_lang.i18n import t
from init_db_core import init_db
from utils.env_helpers import get_env_bool, get_env_int, get_env_str
from utils.github_service import fetch_repo_info
from web import create_app
from database import close_db  # ✅ DB-Teardown importieren

# --- Application-Factory: App-Objekt (für Gunicorn/Railway!) ---
app = create_app()
app.teardown_appcontext(close_db)  # ✅ Automatisches Schließen von DB-Verbindungen
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
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
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

        asyncio.run(run_bot())
    except Exception as e:
        log_error("Discord-Bot", e)


def cleanup():
    logging.info("🔻 Anwendung wird beendet.")


def signal_handler(sig, frame):
    logging.info("🛑 SIGINT empfangen. Beende Anwendung...")
    cleanup()
    sys.exit(0)


# --- Main-Start für lokalen Betrieb und Zusatzdienste ---
if __name__ == "__main__":
    try:
        init_db()
        print("✅ Datenbank-Initialisierung erfolgreich.")
        atexit.register(cleanup)
        signal.signal(signal.SIGINT, signal_handler)
        check_github_repo()

        # Discord-Bot optional starten (asynchron im Thread)
        if get_env_bool("ENABLE_DISCORD_BOT", default=True):
            threading.Thread(target=start_discord_bot, daemon=True).start()

        port = get_env_int("PORT", required=False, default=8080)
        debug = False  # <--- Debug-Modus für lokale Entwicklung AKTIV
        logging.info(f"🌐 Starte Webserver auf http://localhost:{port} (Debug={debug})")
        app.run(host="0.0.0.0", port=port, debug=debug)

    except KeyboardInterrupt:
        print("🛑 Manuell unterbrochen.")
    except Exception as e:
        log_error("Main", e)
        raise


# ➕ Healthcheck für Railway/CI/Monitoring
@app.route("/health")
def healthcheck():
    return Response("ok", status=200)
