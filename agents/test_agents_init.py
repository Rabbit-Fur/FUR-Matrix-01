# tests/test_agents_init.py

import pytest
from types import SimpleNamespace
from agents.agenten_loader import init_agents

class DummyDB(dict): pass
class DummySession(dict): pass

def test_agenten_initialisierung():
    db = DummyDB()
    session = DummySession()
    agents = init_agents(db, session)
    assert "reminder" in agents
    assert "translation" in agents
    assert "champion" in agents
    assert "auth" in agents
    assert "log" in agents
