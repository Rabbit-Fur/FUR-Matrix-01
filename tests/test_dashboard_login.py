def test_dashboard_guide_requires_login(client):
    resp = client.get("/dashboard/guide")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/dashboard/login")


def test_dashboard_login_success(client):
    with client.session_transaction() as sess:
        sess["dashboard_user"] = "Burak"
    resp = client.get("/dashboard/guide")
    assert resp.status_code == 200
