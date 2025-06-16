# migrate_sqlite_to_mongo.py

import sqlite3
from datetime import datetime

from database.mongo_client import db
from models.models_mongo import UserModel

# Pfad zur SQLite-Datenbank
SQLITE_DB_PATH = "fur.db"


def migrate_users():
    sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()

    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    print(f"🔄 {len(rows)} User werden migriert...")

    for row in rows:
        try:
            user_data = {
                "discord_id": row["discord_id"],
                "username": row["username"],
                "avatar": row["avatar"],
                "email": row["email"],
                "role_level": row["role_level"],
                "created_at": datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.strptime(row["updated_at"], "%Y-%m-%d %H:%M:%S"),
            }
            user = UserModel(**user_data)
            db["users"].insert_one(user.dict(by_alias=True))
            print(f"✅ {user.username} migriert")
        except Exception as e:
            print(f"❌ Fehler bei {row['username']}: {e}")

    sqlite_conn.close()
    print("🎉 Migration abgeschlossen.")


if __name__ == "__main__":
    migrate_users()
