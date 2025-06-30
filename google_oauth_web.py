import json
import os
from pathlib import Path

from flask import Flask, redirect, request, session
from google_auth_oauthlib.flow import Flow

SCOPES = ["https://www.googleapis.com/auth/calendar"]
REDIRECT_URI = "https://fur-martix.up.railway.app/oauth2callback"
CLIENT_SECRETS_FILE = Path("credentials/client_secret.json")
TOKEN_PATH = Path("token/token.json")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me")


@app.route("/auth/initiate")
def auth_initiate() -> str:
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
    return redirect(authorization_url)


@app.route("/oauth2callback")
def oauth2callback() -> str:
    state = session.get("state")
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI,
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    TOKEN_PATH.parent.mkdir(exist_ok=True)
    TOKEN_PATH.write_text(creds.to_json())
    return "Authentication successful"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
