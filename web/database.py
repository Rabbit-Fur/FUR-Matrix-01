from database.mongo_client import db


def get_db():
    """Return MongoDB database instance."""
    return db
