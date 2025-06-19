# database/mongo_client.py

import os

from pymongo import MongoClient

MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client["furdb"]  # ← das wird im Projekt importiert


def test_connection():
    try:
        client.admin.command("ping")
        print("✅ MongoDB-Verbindung erfolgreich")
    except Exception as e:
        print("❌ MongoDB-Verbindung fehlgeschlagen:", e)
