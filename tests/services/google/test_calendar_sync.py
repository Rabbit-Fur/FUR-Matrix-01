import logging
from unittest.mock import MagicMock

import services.google.calendar_sync as mod


def test_list_upcoming_events(monkeypatch):
    service = MagicMock()
    events = [{"id": "1"}, {"id": "2"}]
    service.events.return_value.list.return_value.execute.return_value = {"items": events}

    result = mod.list_upcoming_events(service=service, calendar_id="cal")

    assert result == events
    service.events.return_value.list.assert_called_once_with(
        calendarId="cal", singleEvents=True, orderBy="startTime", maxResults=2500
    )


def test_list_upcoming_events_missing_service(monkeypatch):
    monkeypatch.setattr(mod, "get_service", lambda: None)
    assert mod.list_upcoming_events(service=None, calendar_id="cal") == []


def test_list_upcoming_events_missing_calendar_id(monkeypatch):
    service = MagicMock()
    monkeypatch.setattr(mod.Config, "GOOGLE_CALENDAR_ID", None)
    assert mod.list_upcoming_events(service=service, calendar_id=None) == []


def test_format_event():
    event = {"summary": "Test", "start": {"dateTime": "2025-01-01T10:00:00Z"}}
    text = mod.format_event(event)
    assert "Test" in text
    assert "2025-01-01" in text


def test_load_credentials_warns_once(monkeypatch, tmp_path, caplog):
    missing = tmp_path / "token.json"
    monkeypatch.setattr(mod, "TOKEN_PATH", missing, raising=False)
    mod._warned_once = False
    with caplog.at_level(logging.WARNING):
        assert mod.load_credentials() is None
    assert "No Google credentials found" in caplog.text
    caplog.clear()
    with caplog.at_level(logging.WARNING):
        assert mod.load_credentials() is None
    assert caplog.text == ""


def test_load_credentials_client_config(monkeypatch, tmp_path, caplog):
    path = tmp_path / "client.json"
    path.write_text(
        "{" "installed" ": {" "client_id" ": " "id" ", " "client_secret" ": " "sec" "}}"
    )
    monkeypatch.setattr(mod, "TOKEN_PATH", path, raising=False)
    mod._warned_once = False
    with caplog.at_level(logging.WARNING):
        assert mod.load_credentials() is None
    assert "client config" in caplog.text
