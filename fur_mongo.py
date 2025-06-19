"""
fur_mongo.py – zentrale MongoDB-Verbindung für das FUR-System
Verbindet sich mit der Datenbank 'furdb' und stellt globale Collection-Zugriffe bereit.
"""

import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# === Nur bei Direktstart .env laden ===
if __name__ == "__main__":
    load_dotenv()

# === Logging-Konfiguration ===
logger = logging.getLogger("fur_mongo")
logging.basicConfig(level=logging.INFO)

# === MongoDB-URI aus Umgebungsvariable ===
MONGO_URI = os.getenv("MONGODB_URI") or "❌MONGODB_URI_NOT_SET"

if "❌" in MONGO_URI:
    raise EnvironmentError("Fehlende Umgebungsvariable MONGODB_URI")

# === Verbindung herstellen ===
try:
    client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
    client.admin.command("ping")
    logger.info("✅ Verbindung zu MongoDB (furdb) erfolgreich.")
    db = client["furdb"]

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
