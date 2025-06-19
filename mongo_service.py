import logging
import os

from pymongo import MongoClient

MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)
logging.getLogger(__name__).info("MongoDB connected: %s", bool(client))

db = client["furdb"]


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
