# scripts/init_memory_modules.py

import logging
import os
from datetime import datetime

from pymongo import MongoClient

# 🔧 MongoDB-Verbindung
MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client["furdb"]
memory_collection = db["memory_contexts"]

# 📦 Zu importierende Module
modules = [
    {
        "_id": "i18n_babel_core",
        "type": "module",
        "tags": ["i18n", "babel", "flask"],
        "description": "Zentrale Babel-Integration für Flask mit LazyString, Locale-Selektor, Jinja-Filtern und Zeitzonen-Support.",
        "code_refs": ["core/memory/i18n.py", "web/__init__.py", "translations/*.json"],
    },
    {
        "_id": "reminder_system",
        "type": "feature",
        "tags": ["reminder", "discord", "notification", "multilingual"],
        "description": "Reminder-Cog mit Discord-DM, Zeitsteuerung, UI-Adminpanel und Mehrsprachigkeit über fur_lang.",
        "code_refs": [
            "discord_bot/cogs/reminder_cog.py",
            "templates/reminders.html",
            "core/tasks/reminder_scheduler.py",
        ],
    },
    {
        "_id": "discord_login_roles",
        "type": "auth",
        "tags": ["discord", "login", "oauth2", "roles", "flask"],
        "description": "Discord-OAuth2-Login mit Rollenerkennung für ADMIN, R4 und R3. Session-Handling, Weiterleitung und persistente Speicherung in MongoDB.",
        "code_refs": ["web/routes/public_routes.py", "config.py", "models/user.py"],
    },
    {
        "_id": "champion_module",
        "type": "automation",
        "tags": ["champion", "poster", "discord", "pillow", "monthly"],
        "description": "Monatliche Auswertung des PvP-Champions. Automatische Poster-Erstellung mit PIL und Webhook-Versand an Discord.",
        "code_refs": ["core/champion/poster_generator.py", "tasks/champion_task.py"],
    },
    {
        "_id": "hall_of_fame_ui",
        "type": "ui",
        "tags": ["hof", "champion", "frontend", "jinja", "flask"],
        "description": "HTML-Seite zur Darstellung der Hall of Fame inklusive dynamischer Champion-Anzeige und Responsive Design.",
        "code_refs": ["templates/hall_of_fame.html", "web/routes/hof_routes.py"],
    },
    {
        "_id": "language_admin_ui",
        "type": "ui",
        "tags": ["i18n", "admin", "translations", "flask"],
        "description": "Admin-Oberfläche zur Verwaltung von Übersetzungen. Ermöglicht Bearbeitung, Vorschau und Export einzelner Sprachschlüssel.",
        "code_refs": ["templates/admin/language_editor.html", "web/routes/admin_language.py"],
    },
    {
        "_id": "core_memory_loader",
        "type": "core",
        "tags": ["gpt", "memory", "mongo", "context"],
        "description": "Ermöglicht das Laden aller Memory-Module aus MongoDB als Kontext für GPT oder Systemmodule.",
        "code_refs": ["core/memory/memory_loader.py"],
    },
]


# 🧠 Memory-Kontexte einfügen
def store_modules():
    now = datetime.utcnow()
    inserted = 0
    for module in modules:
        module["updated_at"] = now
        module.setdefault("created_at", now)
        result = memory_collection.replace_one({"_id": module["_id"]}, module, upsert=True)
        inserted += result.upserted_id is not None or result.modified_count
    return inserted


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        count = store_modules()
        logging.info(f"✅ {count} Memory-Kontexte erfolgreich gespeichert oder aktualisiert.")
    except Exception as e:
        logging.error("❌ Fehler beim Speichern der Memory-Kontexte", exc_info=e)
