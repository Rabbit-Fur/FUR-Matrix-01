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
