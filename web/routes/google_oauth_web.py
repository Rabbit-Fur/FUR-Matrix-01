import logging
import os
import time
from pathlib import Path
from typing import Optional

from flask import Blueprint, Response, redirect, request, session
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# Blueprint definition
oauth_bp = Blueprint("oauth_web", __name__)

# Constants
SCOPES = ["https://www.googleapis.com/auth/calendar"]
_client_config = os.getenv("GOOGLE_CLIENT_CONFIG")
CLIENT_SECRET_FILE = Path(_client_config) if _client_config else None
TOKEN_PATH = Path(os.getenv("GOOGLE_CREDENTIALS_FILE", "/data/google_token.json"))
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
if not REDIRECT_URI:
    raise RuntimeError("GOOGLE_REDIRECT_URI not configured")

# Logger setup
log = logging.getLogger(__name__)

# Fallback for Railway where session can be lost
state_map: dict[str, float] = {}

# ---- Routes ----


@oauth_bp.route("/auth/initiate")
def auth_initiate() -> Response:
    """Start OAuth flow and redirect user to Google."""
    if CLIENT_SECRET_FILE is None or not CLIENT_SECRET_FILE.exists():
        log.error("CLIENT_SECRET_FILE not configured")
        return Response("Missing Google client config", status=500)
    try:
        flow = Flow.from_client_secrets_file(
            str(CLIENT_SECRET_FILE),
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
        )
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        session["oauth_state"] = state
        state_map[state] = time.time()
        log.info("OAuth flow initiated with state: %s", state)
        return redirect(authorization_url)
    except Exception:
        log.exception("Failed to initiate OAuth flow")
        return Response("Failed to initiate OAuth", status=500)


@oauth_bp.route("/oauth2callback")
def oauth2callback() -> Response:
    """Handle OAuth callback and store token."""
    req_state = request.args.get("state")
    stored_state = session.pop("oauth_state", None)

    valid = False
    if req_state and req_state == stored_state:
        valid = True
    elif req_state and req_state in state_map:
        valid = True
        state_map.pop(req_state, None)

    if not valid:
        log.warning("Invalid OAuth state: received %s, expected %s", req_state, stored_state)
        return Response("Invalid OAuth state", status=400)

    if CLIENT_SECRET_FILE is None or not CLIENT_SECRET_FILE.exists():
        log.error("CLIENT_SECRET_FILE not configured")
        return Response("Missing Google client config", status=500)
    try:
        flow = Flow.from_client_secrets_file(
            str(CLIENT_SECRET_FILE),
            scopes=SCOPES,
            state=req_state,
            redirect_uri=REDIRECT_URI,
        )
        flow.fetch_token(authorization_response=request.url)
    except Exception as exc:
        log.exception("OAuth token fetch failed")
        return Response(f"Authentication failed: {exc}", status=400)

    creds = flow.credentials
    try:
        TOKEN_PATH.write_text(creds.to_json())
        log.info("Token successfully saved to %s", TOKEN_PATH)
    except Exception:
        log.exception("Failed to save OAuth credentials to file")
        return Response("Authentication succeeded, but saving token failed.", status=500)

    return Response("Authentication successful")


# ---- Helpers ----


def load_credentials() -> Optional[Credentials]:
    """Load stored credentials from token file."""
    if not TOKEN_PATH.exists():
        log.warning("Token file not found: %s", TOKEN_PATH)
        return None

    try:
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        if creds.expired and creds.refresh_token:
            log.info("Refreshing expired token...")
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
        return creds
    except Exception:
        log.exception("Failed to load or refresh credentials")
        return None


def get_calendar_service():
    """Return Google Calendar service if credentials exist."""
    creds = load_credentials()
    if not creds:
        return None
    try:
        return build("calendar", "v3", credentials=creds, cache_discovery=False)
    except Exception:
        log.exception("Failed to build Google Calendar API service")
        return None


# ---- Module Exports ----

__all__ = ["oauth_bp", "load_credentials", "get_calendar_service"]
