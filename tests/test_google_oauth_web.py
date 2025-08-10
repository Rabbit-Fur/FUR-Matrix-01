import json
import logging

import pytest
from flask import Flask

from web.routes import google_oauth_web as mod
from services.google.exceptions import SyncTokenExpired


def make_app():
    app = Flask(__name__)
    app.secret_key = "test"
    app.register_blueprint(mod.oauth_bp)
    return app


def test_load_credentials_refresh(monkeypatch, tmp_path, caplog):
    path = tmp_path / "token.json"
    data = {
        "token": "old",
        "refresh_token": "r",
        "client_id": "id",
        "client_secret": "secret",
        "token_uri": "https://token",
    }
    path.write_text(json.dumps(data))
    monkeypatch.setattr(mod, "TOKEN_PATH", path, raising=False)

    class FakeCred:
        expired = True
        refresh_token = "r"

        def refresh(self, request):
            data["token"] = "new"

        def to_json(self):
            return json.dumps(data)

    monkeypatch.setattr(
        mod, "Credentials", type("C", (), {"from_authorized_user_file": lambda *a, **k: FakeCred()})
    )
    monkeypatch.setattr(mod, "Request", lambda: object())

    with caplog.at_level(logging.INFO):
        cred = mod.load_credentials()
    assert isinstance(cred, FakeCred)
    assert json.loads(path.read_text())["token"] == "new"
    assert "Refreshing expired token" in caplog.text


def test_load_credentials_missing_file(monkeypatch, tmp_path, caplog):
    missing = tmp_path / "missing.json"
    monkeypatch.setattr(mod, "TOKEN_PATH", missing, raising=False)
    with caplog.at_level(logging.WARNING):
        with pytest.raises(SyncTokenExpired):
            mod.load_credentials()
    assert "Token file not found" in caplog.text


# ----- Route tests -----


def test_auth_initiate_success(tmp_path, monkeypatch):
    app = make_app()
    client = app.test_client()
    cfg = tmp_path / "client.json"
    cfg.write_text("{}")
    monkeypatch.setattr(mod, "CLIENT_SECRET_FILE", cfg, raising=False)
    monkeypatch.setattr(mod, "state_map", {}, raising=False)

    class FakeFlow:
        def authorization_url(self, **kwargs):
            return "http://consent", "state123"

    monkeypatch.setattr(mod.Flow, "from_client_secrets_file", lambda *a, **k: FakeFlow())
    resp = client.get("/auth/initiate")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "http://consent"
    with client.session_transaction() as sess:
        assert sess["oauth_state"] == "state123"
    assert "state123" in mod.state_map


def test_auth_initiate_missing_config(monkeypatch):
    app = make_app()
    client = app.test_client()
    monkeypatch.setattr(mod, "CLIENT_SECRET_FILE", None, raising=False)
    resp = client.get("/auth/initiate")
    assert resp.status_code == 500
    assert b"Missing Google client config" in resp.data


def test_oauth2callback_success(tmp_path, monkeypatch):
    app = make_app()
    client = app.test_client()
    cfg = tmp_path / "client.json"
    cfg.write_text("{}")
    token_path = tmp_path / "token.json"
    monkeypatch.setattr(mod, "CLIENT_SECRET_FILE", cfg, raising=False)
    monkeypatch.setattr(mod, "TOKEN_PATH", token_path, raising=False)

    class FakeCred:
        def to_json(self):
            return "{}"

    class FakeFlow:
        def __init__(self):
            self.credentials = FakeCred()

        def fetch_token(self, authorization_response=None):
            self.called = authorization_response

    monkeypatch.setattr(mod.Flow, "from_client_secrets_file", lambda *a, **k: FakeFlow())
    with client.session_transaction() as sess:
        sess["oauth_state"] = "state1"
    mod.state_map["state1"] = 0.0
    resp = client.get("/oauth2callback?state=state1&code=x")
    assert resp.status_code == 200
    assert token_path.read_text() == "{}"
    assert b"Authentication successful" in resp.data


def test_oauth2callback_invalid_state(tmp_path, monkeypatch):
    app = make_app()
    client = app.test_client()
    cfg = tmp_path / "client.json"
    cfg.write_text("{}")
    monkeypatch.setattr(mod, "CLIENT_SECRET_FILE", cfg, raising=False)
    with client.session_transaction() as sess:
        sess["oauth_state"] = "good"
    mod.state_map["good"] = 0.0
    resp = client.get("/oauth2callback?state=bad")
    assert resp.status_code == 400
    assert b"Invalid OAuth state" in resp.data


def test_oauth2callback_fetch_failure(tmp_path, monkeypatch):
    app = make_app()
    client = app.test_client()
    cfg = tmp_path / "client.json"
    cfg.write_text("{}")
    monkeypatch.setattr(mod, "CLIENT_SECRET_FILE", cfg, raising=False)

    class FakeFlow:
        def __init__(self):
            self.credentials = None

        def fetch_token(self, authorization_response=None):
            raise RuntimeError("fail")

    monkeypatch.setattr(mod.Flow, "from_client_secrets_file", lambda *a, **k: FakeFlow())
    with client.session_transaction() as sess:
        sess["oauth_state"] = "good"
    mod.state_map["good"] = 0.0
    resp = client.get("/oauth2callback?state=good")
    assert resp.status_code == 400
    assert resp.is_json
    assert resp.json["error"].startswith("Authentication failed")
    assert resp.json["details"] == "fail"


def test_oauth2callback_save_failure(tmp_path, monkeypatch):
    app = make_app()
    client = app.test_client()
    cfg = tmp_path / "client.json"
    cfg.write_text("{}")
    bad_path = tmp_path / "missing" / "token.json"
    monkeypatch.setattr(mod, "CLIENT_SECRET_FILE", cfg, raising=False)
    monkeypatch.setattr(mod, "TOKEN_PATH", bad_path, raising=False)

    class FakeCred:
        def to_json(self):
            return "{}"

    class FakeFlow:
        def __init__(self):
            self.credentials = FakeCred()

        def fetch_token(self, authorization_response=None):
            pass

    monkeypatch.setattr(mod.Flow, "from_client_secrets_file", lambda *a, **k: FakeFlow())
    with client.session_transaction() as sess:
        sess["oauth_state"] = "state1"
    mod.state_map["state1"] = 0.0
    resp = client.get("/oauth2callback?state=state1")
    assert resp.status_code == 500
    assert b"saving token failed" in resp.data
