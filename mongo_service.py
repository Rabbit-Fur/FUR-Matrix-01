
import logging
import warnings

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError

from utils.env_helpers import get_env_str

logger = logging.getLogger(__name__)

MONGO_URI = get_env_str("MONGODB_URI", required=False)
MONGO_DB = get_env_str("MONGO_DB", required=False) 

if not MONGO_URI:
    warnings.warn(
        "MONGODB_URI not set, falling back to local MongoDB URI",
        RuntimeWarning,
    )
    logger.warning("MONGODB_URI not set, using default localhost URI")
    MONGO_URI = "mongodb://localhost:27017"
    MONGO_DB = MONGO_DB or "furdb" 

if not MONGO_DB: 
    raise ConfigurationError("No default database name defined or provided.")

client = MongoClient(MONGO_URI)
logger.info("MongoDB connected: %s", bool(client))

db = client[MONGO_DB]
