import diagnostic_tool as mod
from config import Config


def test_get_channel_mapping(monkeypatch):
    monkeypatch.setattr(Config, "REMINDER_CHANNEL_ID", 1)
    monkeypatch.setattr(Config, "DISCORD_EVENT_CHANNEL_ID", 2)
    monkeypatch.setattr(Config, "EVENT_CHANNEL_ID", 3)
    monkeypatch.setattr(Config, "EVENT_REMINDER_CHANNEL", "events")
    monkeypatch.setattr(Config, "CHAMPION_ANNOUNCEMENT_CHANNEL", "announcements")

    mapping = mod.get_channel_mapping()
    assert mapping["REMINDER_CHANNEL_ID"] == 1
    assert mapping["DISCORD_EVENT_CHANNEL_ID"] == 2
    assert mapping["EVENT_CHANNEL_ID"] == 3


def test_get_poster_files(monkeypatch, tmp_path):
    monkeypatch.setattr(Config, "STATIC_FOLDER", str(tmp_path))
    monkeypatch.setattr(Config, "POSTER_OUTPUT_REL_PATH", "posters")
    monkeypatch.setattr(Config, "CHAMPION_OUTPUT_REL_PATH", "champions")

    (tmp_path / "posters").mkdir()
    (tmp_path / "posters" / "a.png").write_bytes(b"img")
    (tmp_path / "champions").mkdir()
    (tmp_path / "champions" / "b.png").write_bytes(b"img")

    files = mod.get_poster_files()
    assert len(files) == 2


def test_get_log_files(tmp_path):
    (tmp_path / "a.md").write_text("log")
    (tmp_path / "b.md").write_text("log")
    logs = mod.get_log_files(tmp_path)
    assert logs == [str(tmp_path / "a.md"), str(tmp_path / "b.md")]


def test_get_recent_events(monkeypatch):
    def fake_get_events_for(dt):
        return [{"title": "Test", "event_time": "2025-01-01T12:00:00"}]

    def fake_format_events(ev):
        return "ok"

    monkeypatch.setattr(mod.event_helpers, "get_events_for", fake_get_events_for)
    monkeypatch.setattr(mod.event_helpers, "format_events", fake_format_events)
    assert mod.get_recent_events() == "ok"
