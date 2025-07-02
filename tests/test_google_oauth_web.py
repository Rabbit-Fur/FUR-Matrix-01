import json
import logging

from web.routes import google_oauth_web as mod


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
        assert mod.load_credentials() is None
    assert "Token file not found" in caplog.text
