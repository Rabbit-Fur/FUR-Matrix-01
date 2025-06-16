import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

MONGO_USER = "maimarcelgpt"
MONGO_PASS = os.getenv("MONGO_PASSWORD")  # z. B. aus .env geladen
CLUSTER = "furdb.qbrvzgp"
DB = "furdb"

uri = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@{CLUSTER}.mongodb.net/{DB}?retryWrites=true&w=majority&appName=FURdb"

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("✅ MongoDB-Verbindung erfolgreich")
except Exception as e:
    print("❌ Fehler bei MongoDB-Verbindung:", e)
