"""MongoDB initialization helpers for FUR system."""

from database.mongo_client import db


def get_db_connection():
    """Return MongoDB database instance."""
    return db


def init_db():
    """Placeholder for MongoDB initialization."""
    return None
