import json

from agents.translation_agent import TranslationAgent


def test_sync_adds_missing_keys(tmp_path):
    lang_dir = tmp_path / "translations"
    lang_dir.mkdir()
    (lang_dir / "en.json").write_text(json.dumps({"hello": "Hello"}))
    (lang_dir / "de.json").write_text(json.dumps({}))

    agent = TranslationAgent(lang_dir=lang_dir)
    agent.sync()

    data = json.loads((lang_dir / "de.json").read_text())
    assert data.get("hello") == ""


def test_auto_translate_missing(monkeypatch, tmp_path):
    lang_dir = tmp_path / "translations"
    lang_dir.mkdir()
    (lang_dir / "en.json").write_text(json.dumps({"hello": "Hello"}))
    (lang_dir / "de.json").write_text(json.dumps({"hello": ""}))

    from i18n_tools import auto_fill

    def fake_translate(text: str, target: str) -> str:
        return f"{target}:{text}"

    monkeypatch.setattr(auto_fill, "TRANSLATIONS_DIR", lang_dir)
    monkeypatch.setattr(auto_fill, "translate", fake_translate)

    agent = TranslationAgent(lang_dir=lang_dir)
    agent.auto_translate_missing()

    data = json.loads((lang_dir / "de.json").read_text())
    assert data["hello"] == "de:Hello"
