from __future__ import annotations

from flask_socketio import Namespace, SocketIO, emit

socketio = SocketIO(async_mode="threading")


class UpdatesNamespace(Namespace):
    def on_connect(self) -> None:
        emit("connected", {"status": "ok"})

    def on_disconnect(self) -> None:  # pragma: no cover - no logic
        pass


def init_socketio(app) -> SocketIO:
    socketio.init_app(app)
    socketio.on_namespace(UpdatesNamespace("/updates"))
    return socketio


def emit_new_event(event: dict) -> None:
    socketio.emit("new_event", event, namespace="/updates")


def emit_new_reminder(reminder: dict) -> None:
    socketio.emit("new_reminder", reminder, namespace="/updates")
