import os
import time

"""Minimal OAuth2 helper used for standalone tests.

This script mirrors the blueprint in ``web/routes/google_oauth_web.py`` but
keeps the dependencies light. Tokens are stored under ``/data`` so that the
Railway container can mount a persistent volume.  Storing the JSON output of
``Credentials.to_json()`` avoids insecure pickle usage and allows easy refresh
via ``google.oauth2.credentials``.
"""

import logging
from pathlib import Path

from flask import Flask, Response, redirect, request, session
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

log = logging.getLogger(__name__)

# OAuth configuration loaded from environment so the same code works locally
# and on Railway.  ``GOOGLE_CREDENTIALS_FILE`` points to ``/data`` which should be
# backed by a volume in production.
SCOPES = os.getenv(
    "GOOGLE_CALENDAR_SCOPES",
    "https://www.googleapis.com/auth/calendar",
).split(",")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "https://fur-martix.up.railway.app/oauth2callback")
CLIENT_SECRETS_FILE = Path(os.getenv("GOOGLE_CLIENT_CONFIG"))
TOKEN_PATH = Path(os.getenv("GOOGLE_CREDENTIALS_FILE", "/data/google_token.json"))
# Using a JSON file avoids pickle security issues and works across container
# restarts. In production consider storing this JSON in MongoDB instead of the
# ephemeral filesystem.

# ``state`` fallback store for lost Flask sessions (Railway restarts drop memory)
state_map: dict[str, float] = {}

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me")


@app.route("/auth/initiate")
def auth_initiate() -> str:
    """Redirect the user to Google's consent page."""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    session["state"] = state
    # keep the state server side in case the session cookie is lost during a
    # Railway restart
    state_map[state] = time.time()
    log.info("OAuth flow initiated with state %s", state)
    return redirect(authorization_url)


@app.route("/oauth2callback")
def oauth2callback() -> Response:
    """Exchange the authorization code for tokens and persist them."""
    req_state = request.args.get("state")
    stored_state = session.pop("state", None)

    # Validate state parameter to protect against CSRF.  In production we also
    # allow states from ``state_map`` because the Flask session may vanish after
    # a Railway restart.
    valid = False
    if req_state and req_state == stored_state:
        valid = True
    elif req_state and req_state in state_map:
        valid = True
        state_map.pop(req_state, None)

    if not valid:
        log.warning("Invalid OAuth state: %s (expected %s)", req_state, stored_state)
        return Response("Invalid OAuth state", status=400)

    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            state=req_state,
            redirect_uri=REDIRECT_URI,
        )
        flow.fetch_token(authorization_response=request.url)
    except Exception:  # noqa: BLE001
        # Do not leak full exception to the user
        log.exception("OAuth token fetch failed")
        return Response("Authentication failed", status=400)

    creds = flow.credentials
    try:
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_PATH.write_text(creds.to_json())
        log.info("Token stored in %s", TOKEN_PATH)
    except Exception:  # noqa: BLE001
        log.exception("Failed to store OAuth token")
        return Response("Token storage failed", status=500)

    return Response("Authentication successful")


def load_credentials() -> Credentials | None:
    """Return stored credentials and refresh them if necessary."""
    if not TOKEN_PATH.exists():
        log.warning("Token file not found: %s", TOKEN_PATH)
        return None
    try:
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
        return creds
    except Exception:  # noqa: BLE001
        log.exception("Failed to load credentials")
        return None


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
