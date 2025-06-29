import logging
import warnings

from pymongo import MongoClient
from pymongo.errors import ConfigurationError, ConnectionFailure
from pymongo.server_api import ServerApi

from utils.env_helpers import get_env_str

logger = logging.getLogger(__name__)

# --- Konfiguration aus Umgebungsvariablen ---
MONGO_URI = get_env_str("MONGODB_URI", required=False)
MONGO_DB = get_env_str("MONGO_DB", required=False, default="furdb")

# Fallback auf lokale Instanz
if not MONGO_URI:
    warnings.warn(
        "MONGODB_URI not set, falling back to local MongoDB",
        RuntimeWarning,
    )
    logger.warning("MONGODB_URI not set, using default localhost URI")
    MONGO_URI = "mongodb://localhost:27017/furdb"

MONGO_DB = MONGO_DB or "furdb"

# Sicherstellen, dass DB-Name definiert ist
if not MONGO_DB:
    raise ConfigurationError("No default database name defined or provided.")

# --- MongoDB-Client erstellen ---
client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client[MONGO_DB]
if db.name != "furdb":
    raise RuntimeError("\u274c MongoDB DB name must be 'furdb'.")
logger.info("MongoDB connected: %s [DB: %s]", bool(client), MONGO_DB)
logger.info("🔌 Verbunden mit MongoDB-Datenbank: %s", db.name)


# --- Funktionen ---


def test_connection() -> None:
    """Pingt den Server, um die Verbindung zu überprüfen."""
    try:
        client.admin.command("ping")
        logger.info("MongoDB connection OK")
    except ConnectionFailure as exc:
        logger.error("MongoDB connection failed: %s", exc)
        raise


def get_collection(name: str):
    """Gibt eine MongoDB-Collection anhand ihres Namens zurück."""
    return db[name]


def verify_collections(names: list[str] = None):
    """Stellt sicher, dass erforderliche Collections existieren."""
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
            logger.info("Created collection: %s", col)


# --- Direkt ausführbar zum Testen ---
if __name__ == "__main__":
    test_connection()
    verify_collections()
    print("Collections:", db.list_collection_names())
