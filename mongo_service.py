import logging
import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

if __name__ == "__main__":
    load_dotenv()

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    raise RuntimeError("❌ MONGODB_URI nicht gesetzt! Bitte .env prüfen.")

client = MongoClient(MONGO_URI)
logger.info("MongoDB connected: %s", bool(client))

db = client["furdb"]


def test_connection() -> None:
    """Test MongoDB connection and log result."""
    try:
        client.admin.command("ping")
        logger.info("✅ Verbindung zu MongoDB (furdb) erfolgreich.")
    except ConnectionFailure as exc:
        logger.error("❌ Verbindung zu MongoDB fehlgeschlagen: %s", exc)


if __name__ == "__main__":
    test_connection()
    print("📂 Collections:", db.list_collection_names())


def get_collection(name: str):
    """Return MongoDB collection by name."""
    return db[name]


def verify_collections(names=None):
    """Ensure required collections exist."""
    required = names or [
        "users",
        "events",
        "reminders",
        "event_participants",
        "hall_of_fame",
    ]
    existing = db.list_collection_names()
    for col in required:
        if col not in existing:
            db.create_collection(col)
            logging.info("Created collection %s", col)
