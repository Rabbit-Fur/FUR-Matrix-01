"""
agenten_loader.py – Initialisiert alle FUR Agenten zentral
"""

from agents.reminder_agent import ReminderAgent
from agents.translation_agent import TranslationAgent
from agents.champion_agent import ChampionAgent
from agents.auth_agent import AuthAgent
from agents.log_agent import LogAgent

def init_agents(db, session=None):
    return {
        "reminder": ReminderAgent(db),
        "translation": TranslationAgent(),
        "champion": ChampionAgent(db),
        "auth": AuthAgent(session, db),
        "log": LogAgent(db),
    }
