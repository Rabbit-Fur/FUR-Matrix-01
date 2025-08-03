import os
from datetime import datetime
from pymongo import MongoClient
from dateutil import tz

# Mongo-Verbindung aus GitHub Secrets / CI-Umgebung
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB = os.getenv("MONGO_DB", "furdb")

# Aktuelles Datum (lokal Europe/Berlin)
berlin_tz = tz.gettz("Europe/Berlin")
now = datetime.now(tz=berlin_tz)
today_str = now.strftime("%Y-%m-%d")

# MongoDB verbinden
client = MongoClient(MONGO_URL)
db = client[MONGO_DB]
collection = db["daily_logs"]

# Heutiges Log abrufen
log = collection.find_one({"date": today_str})

if not log:
    print(f"⚠️ Kein Log für {today_str} gefunden.")
    exit(0)

# Markdown-Pfad vorbereiten
os.makedirs("logs", exist_ok=True)
filename = f"logs/{today_str}.md"

# Inhalt als Markdown schreiben
with open(filename, "w", encoding="utf-8") as f:
    f.write(f"# 📅 Daily Log – {today_str}\n\n")
    f.write(f"**Erstellt von:** {log.get('created_by', 'Unbekannt')}\n\n")
    for entry in log.get("entries", []):
        f.write(f"### {entry.get('category', 'Allgemein')}\n")
        f.write(f"{entry.get('content', '').strip()}\n\n")

print(f"✅ Log exportiert nach {filename}")
