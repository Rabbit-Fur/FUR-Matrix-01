import json

import google_auth as mod


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
        GOOGLE_CREDENTIALS_FILE=str(cfg_file),
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


def test_load_credentials_refresh(monkeypatch, tmp_path, app):
    path = tmp_path / "token.json"
    app.config.update(GOOGLE_CREDENTIALS_FILE=str(path), GOOGLE_CALENDAR_SCOPES=["scope"])
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

    cred = mod.load_credentials()
    assert isinstance(cred, FakeCred)
    assert refreshed["called"]
    assert json.loads(path.read_text())["token"] == "new"


def test_load_credentials_invalid_returns_none(tmp_path, app):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"web": {"client_id": "id"}}))
    app.config.update(GOOGLE_CREDENTIALS_FILE=str(path), GOOGLE_CALENDAR_SCOPES=["scope"])

    assert mod.load_credentials() is None


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
        GOOGLE_CREDENTIALS_FILE=str(cfg_file),
        GOOGLE_REDIRECT_URI="http://localhost:8080/oauth2callback",
        GOOGLE_CALENDAR_SCOPES=["scope"],
    )

    class FakeCred:
        token = "tok"

    class FakeFlow:
        def __init__(self):
            self.credentials = FakeCred()

        def fetch_token(self, authorization_response=None):
            self.called = authorization_response

    monkeypatch.setattr(
        mod.Flow,
        "from_client_config",
        lambda cfg, scopes, state=None, redirect_uri=None: FakeFlow(),
    )

    class FakeService:
        def userinfo(self):
            return self

        def get(self):
            return self

        def execute(self):
            return {"ok": True}

    monkeypatch.setattr(mod, "build", lambda *a, **k: FakeService())

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
        GOOGLE_CREDENTIALS_FILE=str(cfg_file),
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
