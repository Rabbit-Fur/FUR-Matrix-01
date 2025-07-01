def login_role(client, role: str) -> None:
    with client.session_transaction() as sess:
        sess["user"] = {"role_level": role}
        sess["discord_roles"] = [role]


def clear_session(client) -> None:
    with client.session_transaction() as sess:
        sess.clear()


def get_nav_html(client) -> str:
    resp = client.get("/calendar")
    assert resp.status_code == 200
    return resp.data.decode()


def test_nav_guest_hidden(client):
    clear_session(client)
    html = get_nav_html(client)
    assert "/admin/dashboard" not in html
    assert "/members/dashboard" not in html
    assert "/admin/upload" not in html
    assert "/admin/pet_advisor" not in html
    assert "/admin/memory" not in html


def test_nav_r3_sees_member_only(client):
    clear_session(client)
    login_role(client, "R3")
    html = get_nav_html(client)
    assert "/members/dashboard" in html
    assert "/admin/dashboard" not in html
    assert "/admin/upload" not in html
    assert "/admin/pet_advisor" not in html
    assert "/admin/memory" not in html


def test_nav_r4_sees_admin(client):
    clear_session(client)
    login_role(client, "R4")
    html = get_nav_html(client)
    assert "/members/dashboard" in html
    assert "/admin/dashboard" in html
    assert "/admin/upload" in html
    assert "/admin/pet_advisor" in html
    assert "/admin/memory" not in html


def test_nav_admin_sees_all(client):
    clear_session(client)
    login_role(client, "ADMIN")
    html = get_nav_html(client)
    assert "/members/dashboard" in html
    assert "/admin/dashboard" in html
    assert "/admin/upload" in html
    assert "/admin/pet_advisor" in html
    assert "/admin/memory" in html
