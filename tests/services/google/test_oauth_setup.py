import json

import pytest

import services.google.oauth_setup as mod


def test_main_writes_token_file(tmp_path, monkeypatch):
    token_path = tmp_path / "token.json"
    monkeypatch.setenv("GOOGLE_CREDENTIALS_FILE", str(token_path))
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "secret")
    monkeypatch.setenv("GOOGLE_AUTH_URI", "https://auth")
    monkeypatch.setenv("GOOGLE_TOKEN_URI", "https://token")

    token_data = {
        "token": "tok",
        "refresh_token": "r",
        "token_uri": "https://example/token",
        "client_id": "id",
        "client_secret": "secret",
        "scopes": ["scope"],
    }

    class FakeCred:
        def to_json(self):  # noqa: D401 - not a real docstring
            return json.dumps(token_data)

    class FakeFlow:
        def run_local_server(self, port=0):  # noqa: D401
            return FakeCred()

    monkeypatch.setattr(
        mod,
        "InstalledAppFlow",
        type("F", (), {"from_client_config": lambda *a, **k: FakeFlow()}),
    )

    mod.main()
    data = json.loads(token_path.read_text())
    for key in token_data:
        assert data[key] == token_data[key]


def test_main_requires_client_credentials(tmp_path, monkeypatch):
    token_path = tmp_path / "token.json"
    monkeypatch.setenv("GOOGLE_CREDENTIALS_FILE", str(token_path))
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)

    with pytest.raises(KeyError):
        mod.main()
