from flask import url_for


def login_admin(client):
    with client.session_transaction() as sess:
        sess["user"] = {"role_level": "ADMIN"}


def test_memory_index_requires_admin(client):
    login_admin(client)
    resp = client.get("/admin/memory/")
    assert resp.status_code == 200


def test_memory_detail_displays_dump(app, client):
    login_admin(client)
    from mongo_service import db as _db

    collection = _db["memory_contexts"]
    item_id = collection.insert_one(
        {
            "name": "test",
            "version": "1",
            "tags": ["test"],
            "exported_at": app.config.get("now", __import__("datetime").datetime.utcnow()),
            "content": {"hello": "world"},
        }
    ).inserted_id

    resp = client.get(f"/admin/memory/{item_id}")
    assert resp.status_code == 200
    assert b"hello" in resp.data
    collection.delete_one({"_id": item_id})
