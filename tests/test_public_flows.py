import importlib
import json
from pathlib import Path

import requests

import mongo_service

public_mod = importlib.import_module("blueprints.public")


def get_flashes(client):
    with client.session_transaction() as sess:
        return sess.get("_flashes", [])


def test_discord_login_flow(client, monkeypatch):
    resp = client.get("/login/discord")
    assert resp.status_code == 302
    assert "discord.com/oauth2/authorize" in resp.headers["Location"]
    with client.session_transaction() as sess:
        state = sess["discord_oauth_state"]

    client.application.config.update(
        R3_ROLE_IDS={"1"},
        R4_ROLE_IDS=set(),
        ADMIN_ROLE_IDS=set(),
    )

    class DummyResponse:
        def __init__(self, data, status=200):
            self._data = data
            self.status_code = status
            self.text = json.dumps(data)

        def json(self):
            return self._data

    def fake_post(url, data, headers, timeout):
        assert url == "https://discord.com/api/oauth2/token"
        return DummyResponse({"access_token": "tok"})

    def fake_get(url, headers):
        if url == "https://discord.com/api/users/@me":
            return DummyResponse({"id": "123", "username": "test", "avatar": "x"})
        if url.startswith("https://discord.com/api/users/@me/guilds/"):
            return DummyResponse({"roles": ["1"]})
        raise AssertionError("unexpected url: " + url)

    class FakeCollection:
        def update_one(self, *args, **kwargs):
            self.called = True

    monkeypatch.setattr(requests, "post", fake_post)
    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(mongo_service, "db", {"users": FakeCollection()})
    monkeypatch.setattr(public_mod, "db", {"users": FakeCollection()})

    resp = client.get(f"/callback?code=abc&state={state}")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/members/dashboard")
    flashes = get_flashes(client)
    assert ("success", "Successfully logged in with Discord") in flashes
    with client.session_transaction() as sess:
        assert sess["user"]["id"] == "123"
        assert sess["user"]["role_level"] == "R3"
        assert sess["discord_roles"] == ["R3"]


def test_join_event_requires_login(client):
    client.get("/logout")
    resp = client.post("/events/1/join")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")
    flashes = get_flashes(client)
    assert ("message", "Members only.") in flashes


def test_join_event_success(client):
    with client.session_transaction() as sess:
        sess["user"] = {"id": "42", "role_level": "R3"}
        sess["discord_roles"] = ["R3"]
    resp = client.post("/events/1/join")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/events/1")
    flashes = get_flashes(client)
    assert ("success", "Successfully joined the event!") in flashes


def test_get_champion(client):
    mongo_service.db["hall_of_fame"].insert_one(
        {
            "username": "Foo",
            "month": "2025-06",
            "created_at": __import__("datetime").datetime.utcnow(),
        }
    )
    resp = client.get("/champion")
    assert resp.is_json
    assert resp.status_code == 200
    assert resp.json["username"] == "Foo"


def test_post_reminder(client):
    resp = client.post(
        "/reminder",
        json={
            "user_id": 1,
            "message": "Hi",
            "remind_at": "2025-01-01T00:00:00",
        },
    )
    assert resp.is_json
    assert resp.status_code == 200
    assert resp.json["status"] == "scheduled"


def test_get_poster_image(client, tmp_path, monkeypatch):
    from config import Config

    monkeypatch.setattr(Config, "POSTER_OUTPUT_PATH", str(tmp_path / "posters"))
    posters = Path(Config.POSTER_OUTPUT_PATH)
    posters.mkdir()
    file = posters / "example.png"
    file.write_bytes(b"\x89PNG\r\n\x1a\n")
    resp = client.get("/poster/example.png")
    assert resp.status_code == 200
    assert resp.mimetype == "image/png"
