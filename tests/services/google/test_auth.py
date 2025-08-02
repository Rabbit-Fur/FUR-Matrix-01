import json
import logging
import os

import services.google.auth as mod


def test_google_login_flow(client, tmp_path, monkeypatch):
    config = {
        "web": {
            "client_id": "id",
            "client_secret": "secret",
            "auth_uri": "https://auth",
            "token_uri": "https://token",
        }
    }
    cfg_file = tmp_path / "google.json"
    cfg_file.write_text(json.dumps(config))
    client.application.config.update(
        GOOGLE_CLIENT_CONFIG_FILE=str(cfg_file),
        GOOGLE_REDIRECT_URI="http://localhost:8080/oauth2callback",
        GOOGLE_CALENDAR_SCOPES=["scope"],
    )

    class FakeFlow:
        def authorization_url(self, **kwargs):
            return "http://consent", "state1"

    monkeypatch.setattr(
        mod.Flow,
        "from_client_config",
        lambda cfg, scopes, redirect_uri=None, state=None: FakeFlow(),
    )

    resp = client.get("/auth/google")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "http://consent"
    with client.session_transaction() as sess:
        assert sess["google_oauth_state"] == "state1"


def test_load_credentials_refresh(monkeypatch, tmp_path, app, caplog):
    path = tmp_path / "token.json"
    os.environ["GOOGLE_CREDENTIALS_FILE"] = str(path)
    app.config.pop("GOOGLE_CREDENTIALS_FILE", None)
    app.config.update(GOOGLE_CALENDAR_SCOPES=["scope"])
    data = {
        "token": "old",
        "refresh_token": "r",
        "client_id": "id",
        "client_secret": "secret",
        "token_uri": "https://token",
    }
    path.write_text(json.dumps(data))

    refreshed = {}

    class FakeCred:
        expired = True
        refresh_token = "r"

        def refresh(self, request):
            refreshed["called"] = True

        def to_json(self):
            data["token"] = "new"
            return json.dumps(data)

    monkeypatch.setattr(
        mod.Credentials, "from_authorized_user_info", lambda info, scopes: FakeCred()
    )
    monkeypatch.setattr(mod, "Request", lambda: object())
    with caplog.at_level(logging.INFO):
        cred = mod.load_credentials()
    assert isinstance(cred, FakeCred)
    assert refreshed["called"]
    assert json.loads(path.read_text())["token"] == "new"
    assert f"Loaded Google OAuth credentials from {path}" in caplog.text


def test_load_credentials_invalid_returns_none(tmp_path, app, caplog):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"web": {"client_id": "id"}}))
    os.environ["GOOGLE_CREDENTIALS_FILE"] = str(path)
    app.config.pop("GOOGLE_CREDENTIALS_FILE", None)
    app.config.update(GOOGLE_CALENDAR_SCOPES=["scope"])

    with caplog.at_level(logging.ERROR):
        assert mod.load_credentials() is None
    assert "Invalid credentials" in caplog.text


def test_load_credentials_missing_file(tmp_path, app, caplog):
    missing = tmp_path / "missing.json"
    os.environ["GOOGLE_CREDENTIALS_FILE"] = str(missing)
    app.config.pop("GOOGLE_CREDENTIALS_FILE", None)
    app.config.update(GOOGLE_CALENDAR_SCOPES=["scope"])

    with caplog.at_level(logging.WARNING):
        assert mod.load_credentials() is None
    assert "Token file not found" in caplog.text


def test_oauth2callback_invalid_state(client, tmp_path, monkeypatch):
    cfg_file = tmp_path / "google.json"
    cfg_file.write_text(
        json.dumps({"web": {"client_id": "id", "client_secret": "s", "token_uri": "https://t"}})
    )
    client.application.config.update(GOOGLE_CLIENT_CONFIG_FILE=str(cfg_file))
    with client.session_transaction() as sess:
        sess["google_oauth_state"] = "good"
    resp = client.get("/oauth2callback?state=bad")
    assert resp.status_code == 400
    assert resp.json["error"] == "Invalid OAuth state"


def test_oauth2callback_success(client, tmp_path, monkeypatch):
    config = {
        "web": {
            "client_id": "id",
            "client_secret": "secret",
            "auth_uri": "https://auth",
            "token_uri": "https://token",
        }
    }
    cfg_file = tmp_path / "google.json"
    cfg_file.write_text(json.dumps(config))
    client.application.config.update(
        GOOGLE_CLIENT_CONFIG_FILE=str(cfg_file),
        GOOGLE_REDIRECT_URI="http://localhost:8080/oauth2callback",
        GOOGLE_CALENDAR_SCOPES=["scope"],
    )

    class FakeCred:
        def to_json(self):
            return "{}"

    class FakeFlow:
        def __init__(self):
            self.credentials = FakeCred()

        def fetch_token(self, authorization_response=None):
            self.called = authorization_response

    monkeypatch.setattr(
        mod.Flow,
        "from_client_config",
        lambda cfg, scopes, redirect_uri=None, state=None: FakeFlow(),
    )

    class FakeService:
        def calendarList(self):
            class L:
                def list(self_inner):
                    return self_inner

                def execute(self_inner):
                    return {"items": ["c1"]}

            return L()

    class FakeUserInfoService:
        def userinfo(self):
            return self

        def get(self):
            return self

        def execute(self):
            return {"ok": True}

    monkeypatch.setattr(
        mod,
        "build",
        lambda name, *a, **k: FakeService() if name == "calendar" else FakeUserInfoService(),
    )
    monkeypatch.setattr(mod, "_save_credentials", lambda c: None)

    with client.session_transaction() as sess:
        sess["google_oauth_state"] = "good"

    resp = client.get("/oauth2callback?state=good")
    assert resp.status_code == 200
    assert resp.json == {"status": "connected", "calendars": ["c1"]}

    with client.session_transaction() as sess:
        sess["google_oauth_state"] = "state1"

    resp = client.get("/oauth2callback?state=state1&code=abc")
    assert resp.status_code == 200
    assert resp.is_json
    assert resp.json == {"ok": True}


def test_oauth2callback_invalid_state_or_token(client, tmp_path, monkeypatch):
    config = {
        "web": {
            "client_id": "id",
            "client_secret": "secret",
            "auth_uri": "https://auth",
            "token_uri": "https://token",
        }
    }
    cfg_file = tmp_path / "google.json"
    cfg_file.write_text(json.dumps(config))
    client.application.config.update(
        GOOGLE_CLIENT_CONFIG_FILE=str(cfg_file),
        GOOGLE_REDIRECT_URI="http://localhost:8080/oauth2callback",
        GOOGLE_CALENDAR_SCOPES=["scope"],
    )

    class FakeFlow:
        def __init__(self):
            self.credentials = None

        def fetch_token(self, authorization_response=None):
            raise RuntimeError("fail")

    monkeypatch.setattr(
        mod.Flow,
        "from_client_config",
        lambda cfg, scopes, state=None, redirect_uri=None: FakeFlow(),
    )
    monkeypatch.setattr(mod, "build", lambda *a, **k: None)

    with client.session_transaction() as sess:
        sess["google_oauth_state"] = "good"

    resp = client.get("/oauth2callback?state=bad&code=x")
    assert resp.status_code == 400

    with client.session_transaction() as sess:
        sess["google_oauth_state"] = "good"

    resp = client.get("/oauth2callback?state=good&code=x")
    assert resp.status_code == 400
    assert resp.is_json
    assert resp.json["details"] == "fail"
