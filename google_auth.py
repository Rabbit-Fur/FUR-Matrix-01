from __future__ import annotations

import json
import os
from typing import Optional

from flask import Blueprint, current_app, redirect, request, session, url_for
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

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
    creds = Credentials.from_authorized_user_info(data, scopes)
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
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    _save_credentials(creds)
    return redirect(url_for("public.dashboard"))


__all__ = ["google_auth", "load_credentials"]
