import os
from io import BytesIO

from fur_lang.i18n import t
from tests.test_admin_auth import get_flashes, login_with_role


def test_upload_success(client, tmp_path):
    client.application.config.update(UPLOAD_FOLDER=str(tmp_path))
    login_with_role(client, "R4")
    data = {"file": (BytesIO(b"abc"), "pic.png")}
    resp = client.post(
        "/admin/upload",
        data=data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "pic.png" in os.listdir(tmp_path)
    flashes = get_flashes(client)
    _ = t("file_uploaded", default="Datei hochgeladen", lang="de")
    assert any(cat == "success" for cat, _ in flashes)


def test_upload_invalid_extension(client, tmp_path):
    client.application.config.update(UPLOAD_FOLDER=str(tmp_path))
    login_with_role(client, "R4")
    data = {"file": (BytesIO(b"abc"), "x.txt")}
    resp = client.post(
        "/admin/upload",
        data=data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert not os.listdir(tmp_path)
    flashes = get_flashes(client)
    _ = t("invalid_file_type", default="Ungültiger Dateityp", lang="de")
    assert any(cat == "danger" for cat, _ in flashes)


def test_upload_invalid_mimetype(client, tmp_path):
    client.application.config.update(UPLOAD_FOLDER=str(tmp_path))
    login_with_role(client, "R4")
    data = {"file": (BytesIO(b"abc"), "pic.jpg", "text/plain")}
    resp = client.post(
        "/admin/upload",
        data=data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert not os.listdir(tmp_path)
    flashes = get_flashes(client)
    assert any(cat == "danger" for cat, _ in flashes)


def test_upload_too_large(client, tmp_path):
    client.application.config.update(UPLOAD_FOLDER=str(tmp_path), MAX_CONTENT_LENGTH=5)
    login_with_role(client, "R4")
    data = {"file": (BytesIO(b"abcdef"), "big.png")}
    resp = client.post(
        "/admin/upload",
        data=data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert not os.listdir(tmp_path)
    flashes = get_flashes(client)
    _ = t("file_too_large", default="Datei zu groß", lang="de")
    assert any(cat == "danger" for cat, _ in flashes)
