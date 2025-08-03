def test_dashboard_requires_login(client):
    resp = client.get("/dashboard")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")


def test_dashboard_access_with_login(client):
    with client.session_transaction() as sess:
        sess["user"] = {"id": "1"}
    resp = client.get("/dashboard")
    assert resp.status_code == 200
