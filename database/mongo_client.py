# database/mongo_client.py

from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os

# Verbindung aus Umgebungsvariablen oder direkt setzen
MONGODB_URI = os.getenv("MONGODB_URI") or (
    "mongodb+srv://maimarcelgpt:rC3LJVAnnD0Lii0f@furdb.qbrvzgp.mongodb.net/furdb"
    "?retryWrites=true&w=majority&appName=FURdb"
)

# MongoDB-Client initialisieren
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))

# Datenbank auswählen (furdb)
db = client["furdb"]

# Testverbindung
def test_connection():
    try:
        client.admin.command("ping")
        print("✅ MongoDB-Verbindung erfolgreich")
    except Exception as e:
        print("❌ MongoDB-Verbindung fehlgeschlagen:", e)

# Optional beim Import testen
if __name__ == "__main__":
    test_connection()
