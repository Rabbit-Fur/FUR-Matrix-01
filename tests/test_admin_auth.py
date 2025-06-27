import mongo_service


def login_with_role(client, role):
    with client.session_transaction() as sess:
        sess["user"] = {"role_level": role}
        sess["discord_roles"] = [role]
        sess.pop("_flashes", None)


def get_flashes(client):
    with client.session_transaction() as sess:
        return sess.get("_flashes", [])


def _check_requires_r4(client, method, path):
    client.get("/logout")
    resp = client.open(path, method=method)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")
    # require_roles decorator redirects without flash on missing roles

    # login as R3
    login_with_role(client, "R3")
    resp = client.open(path, method=method)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")

    # login as R4
    login_with_role(client, "R4")
    resp = client.open(path, method=method)
    client.get("/logout")
    return resp


def test_trigger_reminder_requires_r4(client):
    resp = _check_requires_r4(client, "POST", "/admin/trigger_reminder")
    assert resp.status_code == 200
    assert resp.data == b"Reminder triggered"


def test_trigger_champion_post_requires_r4(client):
    resp = _check_requires_r4(client, "POST", "/admin/trigger_champion_post")
    assert resp.status_code == 200
    assert resp.data == b"Champion post triggered"


def test_healthcheck_requires_r4(client):
    resp = _check_requires_r4(client, "POST", "/admin/healthcheck")
    assert resp.status_code == 200
    assert resp.data == b"ok"


def test_export_participants_requires_r4(client):
    resp = _check_requires_r4(client, "GET", "/admin/export_participants")
    assert resp.status_code == 200
    assert resp.mimetype == "text/csv"


def test_export_scores_requires_r4(client):
    resp = _check_requires_r4(client, "GET", "/admin/export_scores")
    assert resp.status_code == 200
    assert resp.mimetype == "text/csv"


def test_post_event_requires_r4(client):
    import importlib

    admin_mod = importlib.import_module("blueprints.admin")
    admin_mod.db = mongo_service.db
    collection = mongo_service.db["events"]
    event_id = collection.insert_one(
        {"title": "T", "description": "d", "event_time": "soon"}
    ).inserted_id
    resp = _check_requires_r4(client, "POST", f"/admin/events/post/{event_id}")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/admin/events")
    collection.delete_one({"_id": event_id})
