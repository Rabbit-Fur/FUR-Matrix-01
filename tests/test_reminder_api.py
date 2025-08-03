import importlib
import sys
import types

from bson import ObjectId


def login_r4(client):
    with client.session_transaction() as sess:
        sess["discord_user"] = {"role_level": "ADMIN"}
        sess["discord_roles"] = ["ADMIN"]


class DummyCollection:
    def __init__(self):
        self.called = None

    def update_one(self, flt, update):
        self.called = (flt, update)


def load_blueprint(monkeypatch):
    stub_bot_main = types.SimpleNamespace(bot=None)
    monkeypatch.setitem(sys.modules, "bot.bot_main", stub_bot_main)
    monkeypatch.setitem(sys.modules, "discord_util", types.ModuleType("discord_util"))
    if "blueprints.reminder_api" in sys.modules:
        del sys.modules["blueprints.reminder_api"]
    return importlib.import_module("blueprints.reminder_api")


def test_deactivate_valid(client, monkeypatch):
    login_r4(client)
    dummy = DummyCollection()
    mod = load_blueprint(monkeypatch)
    monkeypatch.setattr(mod, "get_collection", lambda name: dummy)
    reminder_id = str(ObjectId())
    with client.application.test_request_context("/"):
        import flask

        flask.session["discord_user"] = {"role_level": "ADMIN"}
        flask.session["discord_roles"] = ["ADMIN"]
        resp = mod.deactivate_reminder(reminder_id)
    assert resp.is_json
    assert resp.status_code == 200
    assert dummy.called[0]["_id"] == ObjectId(reminder_id)
    assert resp.json["status"] == "deactivated"


def test_deactivate_invalid_id(client, monkeypatch):
    login_r4(client)
    dummy = DummyCollection()
    mod = load_blueprint(monkeypatch)
    monkeypatch.setattr(mod, "get_collection", lambda name: dummy)
    with client.application.test_request_context("/"):
        import flask

        flask.session["discord_user"] = {"role_level": "ADMIN"}
        flask.session["discord_roles"] = ["ADMIN"]
        resp = mod.deactivate_reminder("foo")

    response, status = resp
    assert status == 400
    assert response.is_json
    assert response.get_json()["error"] == "Invalid ObjectId"
    assert dummy.called is None
