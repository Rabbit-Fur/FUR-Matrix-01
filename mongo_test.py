# mongo_test.py

import os
import logging
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# .env laden
load_dotenv()

# URI aus Umgebungsvariable lesen
uri = os.getenv("MONGODB_URI")

if not uri:
    raise ValueError("❌ MONGODB_URI ist nicht gesetzt. Bitte in der .env-Datei angeben.")

# MongoDB-Client erstellen
client = MongoClient(uri, server_api=ServerApi("1"))
log = logging.getLogger(__name__)

# Verbindung testen
try:
    client.admin.command("ping")
    log.info("✅ Verbindung zu MongoDB Atlas erfolgreich!")
except Exception as e:
    log.error("❌ Verbindung fehlgeschlagen: %s", e)
