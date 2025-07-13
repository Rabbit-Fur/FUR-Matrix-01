import json

import google_oauth_setup as mod


def test_main_writes_token_file(tmp_path, monkeypatch):
    token_path = tmp_path / "token.json"
    cfg = tmp_path / "client.json"
    cfg.write_text("{}")
    monkeypatch.setenv("GOOGLE_CREDENTIALS_FILE", str(token_path))
    monkeypatch.setenv("GOOGLE_CLIENT_CONFIG", str(cfg))

    class FakeCred:
        def to_json(self):
            return json.dumps({"ok": True})

    class FakeFlow:
        def run_local_server(self, port=0):  # noqa: D401
            return FakeCred()

    monkeypatch.setattr(
        mod,
        "InstalledAppFlow",
        type("F", (), {"from_client_secrets_file": lambda *a, **k: FakeFlow()}),
    )

    mod.main()
    assert json.loads(token_path.read_text()) == {"ok": True}
