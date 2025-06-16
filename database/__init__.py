from .mongo_client import db


def close_db(e=None):
    """MongoDB uses connection pooling; nothing to close."""
    return None
