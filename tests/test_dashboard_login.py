def test_dashboard_guide_requires_login(client):
    resp = client.get("/dashboard/guide")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/dashboard/login")


def test_dashboard_login_success(client):
    resp = client.post(
        "/dashboard/login",
        data={"username": "Burak", "password": "Var"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/dashboard/guide")
    # subsequent access should succeed
    resp = client.get("/dashboard/guide")
    assert resp.status_code == 200
    assert b"Dashboard Guide" in resp.data
