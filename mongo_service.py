import logging
import warnings

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from utils.env_helpers import get_env_str

logger = logging.getLogger(__name__)

MONGO_URI = get_env_str("MONGODB_URI", required=False)
if not MONGO_URI:
    warnings.warn(
        "MONGODB_URI not set, falling back to local MongoDB URI",
        RuntimeWarning,
    )
    logger.warning("MONGODB_URI not set, using default localhost URI")
    MONGO_URI = "mongodb://localhost:27017/furdb"

client = MongoClient(MONGO_URI)
logger.info("MongoDB connected: %s", bool(client))

db = client["furdb"]


def test_connection() -> None:
    """Ping the server to verify the connection."""
    try:
        client.admin.command("ping")
        logger.info("MongoDB connection OK")
    except ConnectionFailure as exc:
        logger.error("MongoDB connection failed: %s", exc)


if __name__ == "__main__":
    test_connection()
    print("Collections:", db.list_collection_names())


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
