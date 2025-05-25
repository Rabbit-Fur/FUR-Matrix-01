"""
champion_data.py – Champion-Management für Hall-of-Fame und Poster-Funktion

Stellt Datenhaltung und Zugriffsfunktionen für die aktuellen und historischen Champions bereit.
Wird für automatische Poster-Generierung und Hall-of-Fame-Features genutzt.
"""

from datetime import datetime
from typing import List, Dict, Optional

# Interner Champion-Datenspeicher
champions: List[Dict[str, str]] = [
    {
        "username": "Xevi",
        "honor_title": "🔥 Champion of the Month 🔥",
        "month": "Mai 2025",
        "poster_url": "/static/champions/xevi_april2025.png",
        "created_at": datetime.utcnow().isoformat()
    }
]

def get_latest_champion() -> Optional[Dict[str, str]]:
    """
    Gibt das aktuellste Champion-Objekt zurück (letzter Eintrag).

    Returns:
        dict | None: Champion-Daten (username, honor_title, month, poster_url, created_at) oder None, falls keine Champions vorhanden.
    """
    return champions[-1] if champions else None

def add_champion(username: str, honor_title: str, month: str, poster_url: str) -> None:
    """
    Fügt einen neuen Champion-Datensatz hinzu.

    Args:
        username (str): Spielername.
        honor_title (str): Ehrentitel.
        month (str): Monat/Jahr.
        poster_url (str): Pfad zum Posterbild.

    Returns:
        None
    """
    champions.append({
        "username": username,
        "honor_title": honor_title,
        "month": month,
        "poster_url": poster_url,
        "created_at": datetime.utcnow().isoformat()
    })

def get_all_champions() -> List[Dict[str, str]]:
    """
    Gibt eine Liste aller Champions zurück (älteste zuerst).

    Returns:
        list: Liste aller Champion-Dicts.
    """
    return champions[:]
