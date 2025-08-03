routes = [
    "/",
    "/dashboard",
    "/events",
    "/leaderboard",
    "/hall_of_fame",
    "/lore",
    "/admin/dashboard",
    "/members/dashboard",
]


def test_no_german_words(client):
    with client.session_transaction() as sess:
        sess["lang"] = "en"
        sess["user"] = {"id": "1", "role_level": "ADMIN"}
    for route in routes:
        resp = client.get(route)
        assert resp.status_code == 200
        content = resp.get_data(as_text=True)
        assert "Benutzer" not in content
        assert "Einstellungen" not in content
        assert "Kalender" not in content
        assert "Abmelden" not in content
