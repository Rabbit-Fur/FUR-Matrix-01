# core/logging/memory_logger.py

import logging
from datetime import datetime
from typing import Literal

from mongo_service import get_collection

log = logging.getLogger(__name__)

# Typ für erlaubte Aktionen
MemoryAction = Literal["create", "update", "delete", "read", "sync"]


def log_memory_change(_id: str, action: MemoryAction, data: dict) -> bool:
    """
    Protokolliert eine Änderung im Memory-Modul in der MongoDB-Collection 'memory_logs'.

    Args:
        _id (str): Die ID des Memory-Eintrags.
        action (Literal): Die Aktion, z. B. "create", "update", "delete", "read", "sync".
        data (dict): Die betroffenen oder geänderten Daten.

    Returns:
        bool: True bei Erfolg, False bei Fehler.
    """
    try:
        result = get_collection("memory_logs").insert_one(
            {"memory_id": _id, "action": action, "data": data, "timestamp": datetime.utcnow()}
        )
        log.debug(f"[MemoryLog] ✅ {action.upper()} für {_id} gespeichert: {result.inserted_id}")
        return True
    except Exception as e:
        log.error(f"[MemoryLog] ❌ Fehler bei {action.upper()} für {_id}: {e}")
        return False
