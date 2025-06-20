"""MongoDB initialization helpers for FUR system."""

from mongo_service import db, verify_collections


def get_db_connection():
    """Return MongoDB database instance."""
    return db


def init_db():
    """Initialize MongoDB collections if missing."""
    verify_collections()
