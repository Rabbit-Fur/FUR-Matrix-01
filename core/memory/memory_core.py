"""
memory_core.py – Zentrale API für GPT-Memory-Kontexte im FUR SYSTEM

Erlaubt das Speichern, Abrufen und Listen von Memory-Blöcken
in der MongoDB-Collection `memory_contexts`.
"""

from datetime import datetime
from database.mongo_client import db

memory_collection = db["memory_contexts"]

def store_memory_context(key: str, data: dict) -> None:
    """
    Speichert oder aktualisiert einen Memory-Kontext in der Datenbank.

    Args:
        key (str): Eindeutiger Identifier (_id) des Kontextes.
        data (dict): Die gespeicherten Daten (inkl. Beschreibung, Typ, Tags).
    """
    data["_id"] = key
    data["updated_at"] = datetime.utcnow()
    data.setdefault("created_at", data["updated_at"])
    memory_collection.replace_one({"_id": key}, data, upsert=True)


def get_memory_context(key: str) -> dict:
    """
    Ruft einen gespeicherten Memory-Kontext anhand seines Keys ab.

    Args:
        key (str): Der Identifier (_id) des Kontextes.

    Returns:
        dict: Der gespeicherte Kontext oder ein leerer Dict.
    """
    return memory_collection.find_one({"_id": key}) or {}


def list_memory_contexts(tag: str = None) -> list[dict]:
    """
    Listet alle gespeicherten Memory-Kontexte, optional gefiltert nach Tag.

    Args:
        tag (str, optional): Tag-Filter (z. B. "reminder", "champion").

    Returns:
        list[dict]: Liste der passenden Kontexte.
    """
    if tag:
        return list(memory_collection.find({"tags": tag}))
    return list(memory_collection.find())
