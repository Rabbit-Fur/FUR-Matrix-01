"""
main_app.py – Einstiegspunkt für das FUR-System (Web & Discord-Bot)
Korrigierte Imports und sys.path-Fix für jede Python-Umgebung.
"""

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
from init_db_core import init_db
from utils.github_service import fetch_repo_info

# 🌍 Locale setzen (am besten immer UTF-8 für moderne Deployments)
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

# --- Haupt-Start ---
if __name__ == "__main__":
    try:
        init_db()
        print("✅ Datenbank-Initialisierung erfolgreich.")
        atexit.register(cleanup)
        signal.signal(signal.SIGINT, signal_handler)
        check_github_repo()

        app = create_app()

    except KeyboardInterrupt:
        print("🛑 Manuell unterbrochen.")
    except Exception as e:
        log_error("Main", e)
        raise

# ➕ Healthcheck für Railway/CI/Monitoring
from flask import Response
@app.route("/health")
def healthcheck():
    return Response("ok", status=200)
