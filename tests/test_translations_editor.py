import json

from fur_lang import i18n
from tests.test_memory_viewer import login_admin


def test_translations_editor_save(client, app, monkeypatch, tmp_path):
    login_admin(client)
    monkeypatch.setattr(app, "root_path", str(tmp_path))
    translations_dir = tmp_path / "translations"
    translations_dir.mkdir()
    i18n.translations.clear()
    i18n.translations["de"] = {}

    monkeypatch.setattr(i18n, "get_supported_languages", lambda: ["de"])

    resp = client.post("/admin/translations_editor", data={"language": "de"})
    assert resp.status_code == 200

    resp = client.post(
        "/admin/translations_editor",
        data={"language": "de", "translations[greeting]": "Hallo"},
    )
    assert resp.status_code == 200

    saved = json.loads((translations_dir / "de.json").read_text())
    assert saved == {"greeting": "Hallo"}
    assert i18n.translations["de"] == {"greeting": "Hallo"}
