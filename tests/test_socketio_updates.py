from web.socketio_events import emit_new_event, emit_new_reminder, socketio


def test_event_emission(app):
    client = socketio.test_client(app, namespace="/updates")
    emit_new_event({"title": "PyCon"})
    received = client.get_received("/updates")
    assert any(r["name"] == "new_event" and r["args"][0]["title"] == "PyCon" for r in received)
    emit_new_reminder({"message": "Soon"})
    received = client.get_received("/updates")
    assert any(r["name"] == "new_reminder" for r in received)
    client.disconnect(namespace="/updates")
