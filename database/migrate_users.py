# scripts/migrate_users.py

import sqlite3

from database.mongo_client import db


def migrate_users():
    mongo_users = db["users"]

    sqlite_conn = sqlite3.connect("fur.db")
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()

    rows = cursor.execute("SELECT * FROM users").fetchall()
    users = []

    for row in rows:
        user = {
            "discord_id": row["discord_id"],
            "username": row["username"],
            "avatar": row["avatar"],
            "email": row["email"],
            "role_level": row["role_level"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        users.append(user)

    if users:
        result = mongo_users.insert_many(users)
        print(f"✅ {len(result.inserted_ids)} Nutzer migriert.")
    else:
        print("⚠️ Keine Nutzer gefunden.")

    sqlite_conn.close()


if __name__ == "__main__":
    migrate_users()
