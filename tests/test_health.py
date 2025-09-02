"""Tests for the /health endpoint."""

import sys
import types
from flask import Blueprint


class DummySchedulerAgent:
    """Fallback scheduler used to avoid heavy imports."""

    def __init__(self, *_, **__):
        pass


sys.modules.setdefault(
    "agents.scheduler_agent", types.SimpleNamespace(SchedulerAgent=DummySchedulerAgent)
)

sys.modules.setdefault(
    "web.admin.memory_routes",
    types.SimpleNamespace(admin_memory=Blueprint("admin_memory", __name__)),
)

from main_app import app  # noqa: E402


def test_health_endpoint():
    """The /health route should return HTTP 200 with body 'ok'."""
    with app.test_client() as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.get_data(as_text=True) == "ok"
