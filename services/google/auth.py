from __future__ import annotations

import json
import logging
import os
from typing import Any, Optional

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
    """Return the configured path for Google OAuth credentials.

    The value is read from the Flask configuration variable
    ``GOOGLE_CREDENTIALS_FILE`` and falls back to the environment variable of
    the same name. When neither is provided, ``/data/google_token.json`` is
    used.

    Returns:
        str: Absolute file path where OAuth credentials are stored.
    """

    if has_app_context():
        path = current_app.config.get("GOOGLE_CREDENTIALS_FILE")
        if path:
            return path
    return os.environ.get("GOOGLE_CREDENTIALS_FILE", "/data/google_token.json")


def _token_path() -> str:
    """Return the path used to persist OAuth tokens.

    The function prefers the ``GOOGLE_TOKEN_STORAGE_PATH`` configuration or
    environment variable. If it is not set, the path from :func:`_cred_path`
    is used as a fallback for backwards compatibility.

    Returns:
        str: Absolute file path for the OAuth token store.
    """

    if has_app_context():
        path = current_app.config.get("GOOGLE_TOKEN_STORAGE_PATH")
        if path:
            return path
    return os.environ.get("GOOGLE_TOKEN_STORAGE_PATH", _cred_path())


def _client_config() -> dict[str, dict[str, Any]]:
    """Assemble Google OAuth client configuration from environment variables.

    Values are resolved from Flask configuration when available and fall back to
    environment variables. The returned mapping matches the structure expected
    by ``google-auth`` libraries.

    Returns:
        dict: Configuration dictionary for ``Flow.from_client_config``.
    """

    def _get(name: str, default: Optional[str] = None) -> Optional[str]:
        if has_app_context():
            return current_app.config.get(name) or os.environ.get(name, default)
        return os.environ.get(name, default)

    redirect_uri = _get("GOOGLE_REDIRECT_URI")
    return {
        "web": {
            "client_id": _get("GOOGLE_CLIENT_ID"),
            "project_id": _get("GOOGLE_PROJECT_ID"),
            "auth_uri": _get("GOOGLE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": _get("GOOGLE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
            "auth_provider_x509_cert_url": _get(
                "GOOGLE_AUTH_PROVIDER_CERT_URL", "https://www.googleapis.com/v1/certs"
            ),
            "client_secret": _get("GOOGLE_CLIENT_SECRET"),
            "redirect_uris": [redirect_uri] if redirect_uri else [],
        }
    }


def _save_credentials(creds: Credentials) -> None:
    """Persist Google OAuth credentials to disk.

    Args:
        creds (Credentials): OAuth2 credentials to store.
    """

    path = _token_path()
    if not path:
        return
    log.info("Saving Google OAuth credentials to %s", path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(creds.to_json())


def load_credentials() -> Optional[Credentials]:
    """Load stored credentials and refresh if expired.

    Returns:
        Optional[Credentials]: Existing and refreshed credentials or ``None``
        if no credentials are available.
    """

    path = _token_path()
    if not os.path.exists(path):
        log.warning("Token file not found: %s", path)
        return None
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    scopes = current_app.config.get(
        "GOOGLE_CALENDAR_SCOPES", ["https://www.googleapis.com/auth/calendar.readonly"]
    )
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
    """Start the OAuth flow for Google authentication.

    Returns:
        Response: Redirect to the Google OAuth consent screen or an error
        message.
    """

    config = _client_config()
    if not config["web"].get("client_id") or not config["web"].get("client_secret"):
        return "Missing Google client config", 500
    log.info("Starting Google OAuth flow")
    redirect_uri = config["web"].get("redirect_uris", [None])[0]
    flow = Flow.from_client_config(
        config,
        scopes=current_app.config.get(
            "GOOGLE_CALENDAR_SCOPES",
            ["https://www.googleapis.com/auth/calendar.readonly"],
        ),
        redirect_uri=redirect_uri,
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
    """Handle the OAuth callback and exchange the authorization code.

    After the user grants access, Google redirects back to this endpoint
    with an authorization code. The function verifies the stored state,
    obtains access tokens, persists them and fetches the user's calendar
    list for confirmation.

    Returns:
        Response: JSON data indicating the connection status or error
        details when the flow fails.
    """

    stored_state = session.pop("google_oauth_state", None)
    req_state = request.args.get("state")
    if not stored_state or stored_state != req_state:
        return jsonify({"error": "Invalid OAuth state"}), 400
    log.info("Received OAuth callback with state %s", req_state)

    config = _client_config()
    if not config["web"].get("client_id") or not config["web"].get("client_secret"):
        return jsonify({"error": "Missing Google client config"}), 500

    flow = Flow.from_client_config(
        config,
        scopes=current_app.config.get(
            "GOOGLE_CALENDAR_SCOPES",
            ["https://www.googleapis.com/auth/calendar.readonly"],
        ),
        state=stored_state,
        redirect_uri=config["web"].get("redirect_uris", [None])[0],
    )

    try:
        flow.fetch_token(authorization_response=request.url)
    except (google_exceptions.GoogleAuthError, ValueError) as exc:  # noqa: F841
        status = getattr(getattr(exc, "response", None), "status", None)
        text = getattr(getattr(exc, "response", None), "text", None)
        current_app.logger.warning("OAuth user error: %s status=%s", exc, status)
        if text:
            current_app.logger.debug("Response text: %s", text)
        return jsonify({"error": str(exc), "details": text}), 400
    except Exception as exc:  # noqa: F841 - pragma: no cover - unexpected errors
        status = getattr(getattr(exc, "response", None), "status", None)
        text = getattr(getattr(exc, "response", None), "text", None)
        current_app.logger.exception("OAuth unexpected error")
        if status is not None:
            current_app.logger.error("Response status: %s", status)
        if text:
            current_app.logger.error("Response text: %s", text)
        else:
            text = str(exc)
        return jsonify({"error": "token_failed", "details": text}), 400

    creds = flow.credentials
    try:
        _save_credentials(creds)
    except OSError as exc:
        current_app.logger.exception("Saving credentials failed")
        return jsonify({"error": "Failed to save credentials", "details": str(exc)}), 500
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
