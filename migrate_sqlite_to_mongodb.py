# migrate_sqlite_to_mongodb.py

import sqlite3
import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

# 🔗 SQLite Pfad
SQLITE_PATH = os.path.abspath("app/data/admin_users.db")  # oder aus init_db_core.py

# 🔗 MongoDB
MONGO_URI = os.getenv("DATABASE_URL")
mongo_client = pymongo.MongoClient(MONGO_URI)
mongo_db = mongo_client["furdb"]

# Mappings: Tabellenname → Collectionname
TABLES = {
    "users": "users",
    "events": "events",
    "participants": "participants",
    "reminders": "reminders",
    "hall_of_fame": "hall_of_fame",
    "leaderboard": "leaderboard_entries",
}


def migrate_table(sqlite_conn, table, mongo_collection):
    print(f"📤 Übertrage `{table}` → `{mongo_collection}` ...")
    cursor = sqlite_conn.cursor()
    rows = cursor.execute(f"SELECT * FROM {table}").fetchall()
    columns = [desc[0] for desc in cursor.description]

    docs = [{col: row[i] for i, col in enumerate(columns)} for row in rows]

    if docs:
        mongo_db[mongo_collection].insert_many(docs)
        print(f"✅ {len(docs)} Einträge übertragen")
    else:
        print("⚠️ Keine Daten vorhanden")


def main():
    if not os.path.exists(SQLITE_PATH):
        print(f"❌ SQLite-Datei nicht gefunden: {SQLITE_PATH}")
        return

    conn = sqlite3.connect(SQLITE_PATH)

    for table, collection in TABLES.items():
        try:
            migrate_table(conn, table, collection)
        except Exception as e:
            print(f"❌ Fehler bei `{table}`: {e}")

    conn.close()
    print("✅ Migration abgeschlossen.")


if __name__ == "__main__":
    main()
