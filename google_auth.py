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
    url_for,
)
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
    state = session.pop("google_oauth_state", None)
    if request.args.get("state") != state:
        return jsonify({"error": "invalid_state"}), 400
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
        state=state,
        redirect_uri=current_app.config.get("GOOGLE_REDIRECT_URI"),
    )
    try:
        flow.fetch_token(authorization_response=request.url)
    except Exception:
        current_app.logger.exception("Google OAuth fetch_token failed")
        return jsonify({"error": "token_failed"}), 400
    creds = flow.credentials
    _save_credentials(creds)
    if current_app.config.get("TESTING"):
        service = build("oauth2", "v2", credentials=creds, cache_discovery=False)
        info = service.userinfo().get().execute()
        return jsonify(info)
    return redirect(url_for("public.dashboard"))


__all__ = ["google_auth", "load_credentials"]
