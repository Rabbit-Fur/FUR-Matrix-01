"""
mongo_client.py – stellt die zentrale MongoDB-Verbindung bereit (FURdb)
Wird vom gesamten FUR-System verwendet.
"""

import logging
import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# === .env laden (nur bei direktem Start) ===
if __name__ == "__main__":
    load_dotenv()

# === Logging-Konfiguration ===
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# === MongoDB-Verbindungsdaten aus Umgebungsvariable ===
MONGO_URI = os.getenv("MONGODB_URI")

if not MONGO_URI:
    raise RuntimeError("❌ MONGODB_URI nicht gesetzt! Bitte .env prüfen.")

# === Client erstellen ===
client = MongoClient(MONGO_URI)
db = client["furdb"]


def test_connection():
    """Verbindung testen (für Debug-Zwecke)."""
    try:
        client.admin.command("ping")
        logger.info("✅ Verbindung zu MongoDB (furdb) erfolgreich.")
    except ConnectionFailure as e:
        logger.error(f"❌ Verbindung zu MongoDB fehlgeschlagen: {e}")


# Optionaler Soforttest
if __name__ == "__main__":
    test_connection()
    print("📂 Collections:", db.list_collection_names())
