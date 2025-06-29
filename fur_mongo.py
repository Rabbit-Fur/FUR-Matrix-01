"""
fur_mongo.py – zentrale MongoDB-Verbindung für das FUR-System
Verbindet sich mit der Datenbank 'FURdb' und stellt globale Collection-Zugriffe bereit.
"""

import logging
import warnings

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.server_api import ServerApi

from utils.env_helpers import get_env_str

# === Nur bei Direktstart .env laden ===
if __name__ == "__main__":
    load_dotenv()

# === Logging-Konfiguration ===
logger = logging.getLogger("fur_mongo")
logging.basicConfig(level=logging.INFO)

# === MongoDB-URI aus Umgebungsvariable ===
MONGO_URI = get_env_str("MONGODB_URI", required=False)
MONGO_DB = get_env_str("MONGO_DB", required=False, default="FURdb")
if not MONGO_URI:
    warnings.warn(
        "MONGODB_URI not set, falling back to local MongoDB URI",
        RuntimeWarning,
    )
    logger.warning("MONGODB_URI not set, using default localhost URI")
    MONGO_URI = "mongodb://localhost:27017/FURdb"

# === Verbindung herstellen ===
try:
    client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
    client.admin.command("ping")
    logger.info("✅ Verbindung zu MongoDB (%s) erfolgreich.", MONGO_DB)
    db = client[MONGO_DB]

    # Collection-Verweise
    users = db["users"]
    events = db["events"]
    reminders = db["reminders"]
    hof = db["hall_of_fame"]
    logs = db["logs"]

except ConnectionFailure as e:
    logger.error(f"❌ MongoDB-Verbindung fehlgeschlagen: {e}")
    db = None
    users = events = reminders = hof = logs = None

# === Direktstart: Diagnose-Ausgabe ===
if __name__ == "__main__":
    print("📦 MongoDB verbunden:", bool(db))
    print("📂 Collections:", db.list_collection_names() if db else "❌ keine Verbindung")
