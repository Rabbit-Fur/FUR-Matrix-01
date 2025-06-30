import logging
import time
from pathlib import Path

from flask import Blueprint, Response, redirect, request, session
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

oauth_bp = Blueprint("oauth_web", __name__)

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CLIENT_SECRET_FILE = Path("credentials/client_secret.json")
TOKEN_PATH = Path("token/token.json")
REDIRECT_URI = "https://fur-martix.up.railway.app/oauth2callback"

log = logging.getLogger(__name__)

# Map to store OAuth states in case the session gets lost on Railway
state_map: dict[str, float] = {}


@oauth_bp.route("/auth/initiate")
def auth_initiate() -> Response:
    """Start OAuth flow and redirect user to Google."""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
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
    log.info("OAuth flow initiated with state %s", state)
    return redirect(authorization_url)


@oauth_bp.route("/oauth2callback")
def oauth2callback() -> Response:
    """Handle OAuth callback and store token."""
    req_state = request.args.get("state")
    stored_state = session.pop("oauth_state", None)
    if req_state and req_state == stored_state:
        valid = True
    elif req_state and req_state in state_map:
        valid = True
        state_map.pop(req_state, None)
    else:
        valid = False

    if not valid:
        log.warning("Invalid OAuth state")
        return Response("Invalid OAuth state", status=400)

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        state=req_state,
        redirect_uri=REDIRECT_URI,
    )
    try:
        flow.fetch_token(authorization_response=request.url)
    except Exception as exc:  # pragma: no cover - network issue
        log.exception("OAuth token fetch failed")
        return Response(f"Authentication failed: {exc}", status=400)

    creds = flow.credentials
    TOKEN_PATH.parent.mkdir(exist_ok=True)
    TOKEN_PATH.write_text(creds.to_json())
    log.info("Token stored at %s", TOKEN_PATH)
    return Response("Authentication successful")


def load_credentials() -> Credentials | None:
    """Load stored credentials from token file."""
    if not TOKEN_PATH.exists():
        log.warning("Token file missing")
        return None
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if creds.expired and creds.refresh_token:
        log.info("Refreshing expired token")
        creds.refresh(Request())
        TOKEN_PATH.write_text(creds.to_json())
    return creds


def get_calendar_service():
    """Return Google Calendar service if credentials exist."""
    creds = load_credentials()
    if not creds:
        return None
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


__all__ = ["oauth_bp", "load_credentials", "get_calendar_service"]
