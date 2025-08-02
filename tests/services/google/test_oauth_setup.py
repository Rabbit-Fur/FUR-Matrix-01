import json

import pytest

import services.google.oauth_setup as mod


def test_main_writes_token_file(tmp_path, monkeypatch):
    token_path = tmp_path / "token.json"
    cfg = tmp_path / "client.json"
    cfg.write_text("{}")
    monkeypatch.setenv("GOOGLE_CREDENTIALS_FILE", str(token_path))
    monkeypatch.setenv("GOOGLE_CLIENT_CONFIG", str(cfg))

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
        type("F", (), {"from_client_secrets_file": lambda *a, **k: FakeFlow()}),
    )

    mod.main()
    data = json.loads(token_path.read_text())
    for key in token_data:
        assert data[key] == token_data[key]


def test_main_raises_with_missing_client_config(tmp_path, monkeypatch):
    token_path = tmp_path / "token.json"
    monkeypatch.setenv("GOOGLE_CREDENTIALS_FILE", str(token_path))
    monkeypatch.delenv("GOOGLE_CLIENT_CONFIG", raising=False)

    with pytest.raises(TypeError):
        mod.main()


def test_main_raises_with_invalid_client_config(tmp_path, monkeypatch):
    token_path = tmp_path / "token.json"
    monkeypatch.setenv("GOOGLE_CREDENTIALS_FILE", str(token_path))
    monkeypatch.setenv("GOOGLE_CLIENT_CONFIG", str(tmp_path / "missing.json"))

    with pytest.raises(FileNotFoundError):
        mod.main()
