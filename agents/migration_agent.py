"""
MigrationAgent – prüft und migriert zwischen SQLite und MongoDB
"""
import logging
import sqlite3
from datetime import datetime
from pymongo.database import Database

class MigrationAgent:
    def __init__(self, sqlite_path: str, mongo_db: Database):
        self.sqlite_path = sqlite_path
        self.mongo_db = mongo_db

    def migrate_users(self) -> int:
        """Migriert User-Daten von SQLite nach MongoDB"""
        migrated = 0
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()

            rows = cursor.execute("SELECT discord_id, username, email, role_level FROM users").fetchall()
            for row in rows:
                discord_id, username, email, role_level = row
                self.mongo_db["users"].update_one(
                    {"discord_id": discord_id},
                    {
                        "$set": {
                            "username": username,
                            "email": email,
                            "role_level": role_level,
                            "updated_at": datetime.utcnow()
                        },
                        "$setOnInsert": {
                            "created_at": datetime.utcnow()
                        }
                    },
                    upsert=True
                )
                migrated += 1

            logging.info(f"✅ {migrated} Benutzer erfolgreich migriert.")
        except Exception as e:
            logging.error("❌ Migration fehlgeschlagen: %s", e)
        return migrated
