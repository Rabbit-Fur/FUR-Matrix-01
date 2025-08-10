import logging
import os
import time
from pathlib import Path

from flask import Blueprint, Response, jsonify, redirect, request, session
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# Blueprint definition
oauth_bp = Blueprint("oauth_web", __name__)

# Constants
SCOPES = ["https://www.googleapis.com/auth/calendar"]
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "https://fur-martix.up.railway.app/oauth2callback")
CLIENT_CONFIG = {
    "web": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "auth_uri": os.getenv("GOOGLE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
        "token_uri": os.getenv("GOOGLE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
        "auth_provider_x509_cert_url": os.getenv(
            "GOOGLE_AUTH_PROVIDER_CERT_URL", "https://www.googleapis.com/v1/certs"
        ),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uris": [REDIRECT_URI],
    }
}
TOKEN_PATH = Path(os.getenv("GOOGLE_CREDENTIALS_FILE", "/data/google_token.json"))
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
if not REDIRECT_URI:
    raise RuntimeError("GOOGLE_REDIRECT_URI not configured")

# Logger setup
log = logging.getLogger(__name__)


class SyncTokenExpired(Exception):
    """Raised when stored OAuth credentials are missing or invalid."""

# Fallback for Railway where session can be lost
state_map: dict[str, float] = {}

# ---- Routes ----


@oauth_bp.route("/auth/initiate")
def auth_initiate() -> Response:
    """Start OAuth flow and redirect user to Google."""
    if not CLIENT_CONFIG["web"].get("client_id") or not CLIENT_CONFIG["web"].get("client_secret"):
        log.error("CLIENT_CONFIG incomplete")
        return Response("Missing Google client config", status=500)
    try:
        flow = Flow.from_client_config(
            CLIENT_CONFIG,
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

    if not CLIENT_CONFIG["web"].get("client_id") or not CLIENT_CONFIG["web"].get("client_secret"):
        log.error("CLIENT_CONFIG incomplete")
        return Response("Missing Google client config", status=500)
    try:
        flow = Flow.from_client_config(
            CLIENT_CONFIG,
            scopes=SCOPES,
            state=req_state,
            redirect_uri=REDIRECT_URI,
        )
        flow.fetch_token(authorization_response=request.url)
    except Exception as exc:
        status = getattr(getattr(exc, "response", None), "status", None)
        text = getattr(getattr(exc, "response", None), "text", None)
        log.exception("OAuth token fetch failed")
        if status is not None:
            log.error("Response status: %s", status)
        if text:
            log.error("Response text: %s", text)
        else:
            text = str(exc)
        return jsonify({"error": f"Authentication failed: {exc}", "details": text}), 400

    creds = flow.credentials
    try:
        TOKEN_PATH.write_text(creds.to_json())
        log.info("Token successfully saved to %s", TOKEN_PATH)
    except Exception:
        log.exception("Failed to save OAuth credentials to file")
        return Response("Authentication succeeded, but saving token failed.", status=500)

    return Response("Authentication successful")


# ---- Helpers ----


def load_credentials() -> Credentials:
    """Load stored credentials from token file.

    Raises
    ------
    SyncTokenExpired
        If the token file does not exist or credentials cannot be loaded.
    """

    if not TOKEN_PATH.exists():
        log.warning("Token file not found: %s", TOKEN_PATH)
        raise SyncTokenExpired from None

    try:
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        if creds.expired and creds.refresh_token:
            log.info("Refreshing expired token...")
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
        return creds
    except Exception:
        log.exception("Failed to load or refresh credentials")
        raise SyncTokenExpired from None


def get_calendar_service():
    """Return Google Calendar service if credentials are available.

    Credential loading issues raise :class:`SyncTokenExpired`.
    """

    creds = load_credentials()
    try:
        return build("calendar", "v3", credentials=creds, cache_discovery=False)
    except Exception:
        log.exception("Failed to build Google Calendar API service")
        return None


# ---- Module Exports ----

__all__ = ["oauth_bp", "load_credentials", "get_calendar_service", "SyncTokenExpired"]
