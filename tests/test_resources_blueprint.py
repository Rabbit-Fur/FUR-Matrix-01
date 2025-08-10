from tests.test_admin_auth import login_with_role


def test_resources_requires_login(client):
    client.get("/logout")
    resp = client.get("/resources")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login?next=/resources")


def test_resources_listing_and_download(client, tmp_path):
    client.application.config.update(RESOURCES_FOLDER=str(tmp_path))
    file = tmp_path / "example.txt"
    file.write_text("hello")
    login_with_role(client, "R3")
    resp = client.get("/resources")
    assert resp.status_code == 200
    assert b"example.txt" in resp.data
    resp = client.get("/resources/download/example.txt")
    assert resp.status_code == 200
    assert resp.data == b"hello"
