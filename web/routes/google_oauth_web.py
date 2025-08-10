import logging
import time
from pathlib import Path

from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    redirect,
    request,
    session,
)
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# Blueprint definition
oauth_bp = Blueprint("oauth_web", __name__)

# Constants
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def _redirect_uri() -> str:
    uri = current_app.config.get("GOOGLE_REDIRECT_URI")
    if not uri:
        raise RuntimeError("GOOGLE_REDIRECT_URI not configured")
    return uri


def _client_config() -> dict:
    return {
        "web": {
            "client_id": current_app.config.get("GOOGLE_CLIENT_ID"),
            "project_id": current_app.config.get("GOOGLE_PROJECT_ID"),
            "auth_uri": current_app.config.get("GOOGLE_AUTH_URI"),
            "token_uri": current_app.config.get("GOOGLE_TOKEN_URI"),
            "auth_provider_x509_cert_url": current_app.config.get("GOOGLE_AUTH_PROVIDER_CERT_URL"),
            "client_secret": current_app.config.get("GOOGLE_CLIENT_SECRET"),
            "redirect_uris": [_redirect_uri()],
        }
    }


def _token_path() -> Path:
    return Path(current_app.config.get("GOOGLE_CREDENTIALS_FILE", "/data/google_token.json"))


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
    client_config = _client_config()
    if not client_config["web"].get("client_id") or not client_config["web"].get("client_secret"):
        log.error("CLIENT_CONFIG incomplete")
        return Response("Missing Google client config", status=500)
    try:
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=_redirect_uri(),
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

    client_config = _client_config()
    if not client_config["web"].get("client_id") or not client_config["web"].get("client_secret"):
        log.error("CLIENT_CONFIG incomplete")
        return Response("Missing Google client config", status=500)
    try:
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            state=req_state,
            redirect_uri=_redirect_uri(),
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
    token_path = _token_path()
    try:
        token_path.write_text(creds.to_json())
        log.info("Token successfully saved to %s", token_path)
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

    token_path = _token_path()
    if not token_path.exists():
        log.warning("Token file not found: %s", token_path)
        raise SyncTokenExpired from None

    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if creds.expired and creds.refresh_token:
            log.info("Refreshing expired token...")
            creds.refresh(Request())
            token_path.write_text(creds.to_json())
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
