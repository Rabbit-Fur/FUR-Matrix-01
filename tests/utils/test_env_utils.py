from utils.env_utils import get_google_calendar_settings, DEFAULT_TOKEN_PATH, DEFAULT_SCOPES


def clear_env(monkeypatch):
    for var in [
        "GOOGLE_CALENDAR_ID",
        "GOOGLE_TOKEN_STORAGE_PATH",
        "GOOGLE_CREDENTIALS_FILE",
        "GOOGLE_CALENDAR_SCOPES",
    ]:
        monkeypatch.delenv(var, raising=False)


def test_defaults(monkeypatch):
    clear_env(monkeypatch)
    settings = get_google_calendar_settings()
    assert settings.calendar_id is None
    assert settings.token_path == DEFAULT_TOKEN_PATH
    assert settings.credentials_file == DEFAULT_TOKEN_PATH
    assert settings.scopes == DEFAULT_SCOPES


def test_token_path_fallback(monkeypatch):
    clear_env(monkeypatch)
    monkeypatch.setenv("GOOGLE_CREDENTIALS_FILE", "/tmp/creds.json")
    settings = get_google_calendar_settings()
    assert settings.token_path == "/tmp/creds.json"
    assert settings.credentials_file == "/tmp/creds.json"


def test_overrides(monkeypatch):
    clear_env(monkeypatch)
    monkeypatch.setenv("GOOGLE_CALENDAR_ID", "abc")
    monkeypatch.setenv("GOOGLE_TOKEN_STORAGE_PATH", "/tmp/token.json")
    monkeypatch.setenv("GOOGLE_CREDENTIALS_FILE", "/tmp/creds.json")
    monkeypatch.setenv("GOOGLE_CALENDAR_SCOPES", "s1,s2")
    settings = get_google_calendar_settings()
    assert settings.calendar_id == "abc"
    assert settings.token_path == "/tmp/token.json"
    assert settings.credentials_file == "/tmp/creds.json"
    assert settings.scopes == ["s1", "s2"]
