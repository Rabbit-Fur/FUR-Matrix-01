"""
champion_data.py – Champion-Management für Hall-of-Fame und Poster-Funktion

Stellt Datenhaltung und Zugriffsfunktionen für die aktuellen und historischen Champions bereit.
Wird für automatische Poster-Generierung und Hall-of-Fame-Features genutzt.
"""

from datetime import datetime
from typing import Dict, List, Optional
from database import get_db_connection

def save_champion_to_db(champion: Dict[str, str]) -> None:
    """
    Speichert einen neuen Champion-Eintrag in der Datenbank.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO hall_of_fame (username, honor_title, month, poster_url, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        champion["username"],
        champion["honor_title"],
        champion["month"],
        champion["poster_url"],
        champion.get("created_at", datetime.utcnow().isoformat())
    ))
    conn.commit()
    conn.close()


def load_champions_from_db() -> List[Dict[str, str]]:
    """
    Lädt alle Champion-Einträge aus der Datenbank.

    Returns:
        List[Dict[str, str]]: Liste der Champions (älteste zuerst)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute("""
        SELECT username, honor_title, month, poster_url, created_at
        FROM hall_of_fame ORDER BY created_at ASC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_latest_champion() -> Optional[Dict[str, str]]:
    """
    Gibt das aktuellste Champion-Objekt zurück (letzter Eintrag).

    Returns:
        dict | None: Champion-Daten oder None, falls keine Champions vorhanden.
    """
    champions = load_champions_from_db()
    return champions[-1] if champions else None


def add_champion(username: str, honor_title: str, month: str, poster_url: str) -> None:
    """
    Fügt einen neuen Champion-Datensatz hinzu und speichert ihn in der DB.

    Args:
        username (str): Spielername.
        honor_title (str): Ehrentitel.
        month (str): Monat/Jahr.
        poster_url (str): Pfad zum Posterbild.

    Returns:
        None
    """
    new_champ = {
        "username": username,
        "honor_title": honor_title,
        "month": month,
        "poster_url": poster_url,
        "created_at": datetime.utcnow().isoformat(),
    }
    save_champion_to_db(new_champ)


def get_champion_by_month(month: str) -> Optional[Dict[str, str]]:
    """
    Sucht einen Champion anhand des Monats (z. B. 'Mai 2025').

    Args:
        month (str): Monat als lesbarer String.

    Returns:
        dict | None: Champion oder None, falls nicht gefunden.
    """
    champions = load_champions_from_db()
    for champ in reversed(champions):
        if champ["month"].lower() == month.lower():
            return champ
    return None
