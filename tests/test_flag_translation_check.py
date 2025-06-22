import importlib
import logging

from fur_lang import i18n


def test_warns_when_flag_missing_translation(tmp_path, caplog):
    flags_dir = tmp_path / "static" / "flags"
    flags_dir.mkdir(parents=True)
    (flags_dir / "xx.png").write_bytes(b"img")
    translations_dir = tmp_path / "translations"
    translations_dir.mkdir()
    (translations_dir / "en.json").write_text("{}")

    caplog.set_level(logging.WARNING)

    importlib.reload(i18n)
    caplog.clear()

    i18n.warn_flags_without_translation(str(flags_dir), str(translations_dir))

    assert any(
        "Flag 'xx.png' found but no xx.json translation." in r.message for r in caplog.records
    )
