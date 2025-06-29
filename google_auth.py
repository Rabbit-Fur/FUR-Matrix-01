from __future__ import annotations

import json
import logging
import os
from typing import Optional

from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    request,
    session,
)
from google.auth import exceptions as google_exceptions
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

google_auth = Blueprint("google_auth", __name__)


def _cred_path() -> Optional[str]:
    return current_app.config.get("GOOGLE_CREDENTIALS_FILE")


def _save_credentials(creds: Credentials) -> None:
    path = _cred_path()
    if not path:
        return
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(creds.to_json())


def load_credentials() -> Optional[Credentials]:
    """Load stored credentials and refresh if expired."""
    path = _cred_path()
    if not path or not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    scopes = current_app.config.get(
        "GOOGLE_CALENDAR_SCOPES",
        ["https://www.googleapis.com/auth/calendar.readonly"],
    )
    try:
        creds = Credentials.from_authorized_user_info(data, scopes)
    except ValueError as exc:  # invalid or client config only
        logging.error("Main: %s", exc)
        return None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save_credentials(creds)
    return creds


@google_auth.route("/auth/google")
def auth_google():
    path = _cred_path()
    if not path or not os.path.exists(path):
        return "Missing Google client config", 500
    with open(path, "r", encoding="utf-8") as fh:
        config = json.load(fh)
    flow = Flow.from_client_config(
        config,
        scopes=current_app.config.get(
            "GOOGLE_CALENDAR_SCOPES",
            ["https://www.googleapis.com/auth/calendar.readonly"],
        ),
        redirect_uri=current_app.config.get("GOOGLE_REDIRECT_URI"),
    )
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    session["google_oauth_state"] = state
    return redirect(authorization_url)


@google_auth.route("/oauth2callback")
def oauth2callback():
    stored_state = session.pop("google_oauth_state", None)
    req_state = request.args.get("state")
    if not stored_state or stored_state != req_state:
        return jsonify({"error": "Invalid OAuth state"}), 400

    path = _cred_path()
    if not path or not os.path.exists(path):
        return jsonify({"error": "Missing Google client config"}), 500

    with open(path, "r", encoding="utf-8") as fh:
        config = json.load(fh)

    flow = Flow.from_client_config(
        config,
        scopes=current_app.config.get(
            "GOOGLE_CALENDAR_SCOPES",
            ["https://www.googleapis.com/auth/calendar.readonly"],
        ),
        state=stored_state,
        redirect_uri=current_app.config.get("GOOGLE_REDIRECT_URI"),
    )

    try:
        flow.fetch_token(authorization_response=request.url)
    except (google_exceptions.GoogleAuthError, ValueError) as exc:  # noqa: F841
        current_app.logger.warning("OAuth user error: %s", exc)
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:  # noqa: F841 - pragma: no cover - unexpected errors
        current_app.logger.exception("OAuth unexpected error")
        return jsonify({"error": "token_failed"}), 400

    creds = flow.credentials
    _save_credentials(creds)

    try:
        service = build("calendar", "v3", credentials=creds)
        calendars_resp = service.calendarList().list().execute()
        calendars = calendars_resp.get("items", [])
    except Exception as exc:  # noqa: F841 - pragma: no cover - API failure
        current_app.logger.exception("Fetching calendar list failed")
        return jsonify({"error": "Failed to fetch calendars"}), 500

    if request.args.get("code") and current_app.config.get("TESTING"):
        service = build("oauth2", "v2", credentials=creds, cache_discovery=False)
        info = service.userinfo().get().execute()
        return jsonify(info)

    return jsonify({"status": "connected", "calendars": calendars})


__all__ = ["google_auth", "load_credentials"]
