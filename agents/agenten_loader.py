"""
agenten_loader.py – Initialisiert alle FUR Agenten zentral
"""

from typing import Any, Mapping

from agents.auth_agent import AuthAgent
from agents.champion_agent import ChampionAgent
from agents.log_agent import LogAgent
from agents.reminder_agent import ReminderAgent
from agents.translation_agent import TranslationAgent

Agent = Any


def init_agents(db: Any, session: Mapping | None = None) -> dict[str, "Agent"]:
    """Initialisiert alle registrierten Agenten und gibt sie gebündelt zurück.

    Zweck:
        Bündelt die wichtigsten FUR Agenten und macht sie zentral verfügbar.

    Parameter:
        db (Any): Datenbankschnittstelle, die den Agenten übergeben wird.
        session (Mapping | None, optional): Optionale Session für Authentifizierung.

    Rückgabewert:
        dict[str, Agent]: Wörterbuch mit Agentnamen als Schlüssel und den
        jeweiligen Agent-Instanzen als Werte.
    """

    return {
        "reminder": ReminderAgent(db),
        "translation": TranslationAgent(),
        "champion": ChampionAgent(db),
        "auth": AuthAgent(session, db),
        "log": LogAgent(db),
    }
