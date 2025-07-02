from __future__ import annotations

import json
import logging
import os
from typing import Optional

from flask import (
    Blueprint,
    current_app,
    has_app_context,
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

log = logging.getLogger(__name__)


def _cred_path() -> str:
    if has_app_context():
        path = current_app.config.get("GOOGLE_CREDENTIALS_FILE")
        if path:
            return path
    return os.environ.get("GOOGLE_CREDENTIALS_FILE", "/data/google_token.json")


def _save_credentials(creds: Credentials) -> None:
    path = _cred_path()
    if not path:
        return
    log.info("Saving Google OAuth credentials to %s", path)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(creds.to_json())


def load_credentials() -> Optional[Credentials]:
    """Load stored credentials and refresh if expired."""
    path = _cred_path()
    if not os.path.exists(path):
        log.warning("Token file not found: %s", path)
        return None
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if has_app_context():
        scopes = current_app.config.get(
            "GOOGLE_CALENDAR_SCOPES",
            ["https://www.googleapis.com/auth/calendar.readonly"],
        )
    else:
        scopes = os.environ.get(
            "GOOGLE_CALENDAR_SCOPES",
            "https://www.googleapis.com/auth/calendar.readonly",
        ).split(",")
    try:
        creds = Credentials.from_authorized_user_info(data, scopes)
    except ValueError:
        log.error("Invalid credentials")
        return None
    if creds and creds.expired and creds.refresh_token:
        log.info("Refreshing expired Google credentials")
        creds.refresh(Request())
        _save_credentials(creds)
    log.info("Loaded Google OAuth credentials from %s", path)
    return creds


@google_auth.route("/auth/google")
def auth_google():
    path = _cred_path()
    if not path or not os.path.exists(path):
        return "Missing Google client config", 500
    log.info("Starting Google OAuth flow")
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
    log.debug("OAuth state=%s", state)
    session["google_oauth_state"] = state
    return redirect(authorization_url)


@google_auth.route("/oauth2callback")
def oauth2callback():
    stored_state = session.pop("google_oauth_state", None)
    req_state = request.args.get("state")
    if not stored_state or stored_state != req_state:
        return jsonify({"error": "Invalid OAuth state"}), 400
    log.info("Received OAuth callback with state %s", req_state)

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
    log.info("OAuth flow completed and credentials saved")

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

    log.info("User connected %s calendars", len(calendars))
    return jsonify({"status": "connected", "calendars": calendars})


__all__ = ["google_auth", "load_credentials"]
