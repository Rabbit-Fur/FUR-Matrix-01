# database/mongo_client.py

import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

MONGO_USER = "maimarcelgpt"
MONGO_PASS = os.getenv("MONGO_PASSWORD", "rC3LJVAnnD0Lii0f")
MONGO_CLUSTER = "furdb.qbrvzgp"
MONGO_DB = "furdb"

uri = (
    f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@{MONGO_CLUSTER}.mongodb.net/"
    f"{MONGO_DB}?retryWrites=true&w=majority&appName=FURdb"
)

client = MongoClient(uri, server_api=ServerApi('1'))
db = client[MONGO_DB]  # ← das wird im Projekt importiert

def test_connection():
    try:
        client.admin.command("ping")
        print("✅ MongoDB-Verbindung erfolgreich")
    except Exception as e:
        print("❌ MongoDB-Verbindung fehlgeschlagen:", e)
