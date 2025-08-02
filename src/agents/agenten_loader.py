"""
agenten_loader.py – Initialisiert alle FUR Agenten zentral
"""

from .auth_agent import AuthAgent
from .champion_agent import ChampionAgent
from .log_agent import LogAgent
from .reminder_agent import ReminderAgent
from .translation_agent import TranslationAgent


def init_agents(db, session=None):
    return {
        "reminder": ReminderAgent(db),
        "translation": TranslationAgent(),
        "champion": ChampionAgent(db),
        "auth": AuthAgent(session, db),
        "log": LogAgent(db),
    }
