"""Google OAuth2 helpers with PKCE and token encryption."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import secrets
from typing import Iterable

import requests
from cryptography.fernet import Fernet

_GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


# ---------------------------------------------------------------------------
# PKCE utilities
# ---------------------------------------------------------------------------


def generate_code_verifier(length: int = 128) -> str:
    """Return a secure ``code_verifier`` for PKCE."""
    if length < 43 or length > 128:
        raise ValueError("length must be between 43 and 128")
    # secrets.token_urlsafe returns a base64 string; ensure max length
    verifier = secrets.token_urlsafe(length)
    return verifier[:length]


def generate_code_challenge(verifier: str) -> str:
    """Return ``code_challenge`` for the given verifier."""
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return challenge


# ---------------------------------------------------------------------------
# Authorization helpers
# ---------------------------------------------------------------------------


def build_authorization_url(
    client_id: str,
    redirect_uri: str,
    scopes: Iterable[str],
    state: str,
    code_challenge: str,
) -> str:
    """Return the Google OAuth2 authorization URL."""
    from urllib.parse import urlencode

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(scopes),
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"{_GOOGLE_AUTH_URL}?{urlencode(params)}"


# ---------------------------------------------------------------------------
# Token exchange
# ---------------------------------------------------------------------------


def exchange_code_for_token(
    code: str,
    code_verifier: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    client_secret: str,
) -> dict:
    """Exchange authorization ``code`` for OAuth tokens."""
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
    }
    response = requests.post(_GOOGLE_TOKEN_URL, data=data, timeout=10)
    print(response.status_code)
    print(response.text)
    if response.status_code != 200:
        raise RuntimeError(f"Token exchange failed: {response.text}")
    return response.json()


# ---------------------------------------------------------------------------
# Token encryption helpers
# ---------------------------------------------------------------------------


def _get_fernet(secret_key: str) -> Fernet:
    digest = hashlib.sha256(secret_key.encode()).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_refresh_token(token: str, secret_key: str) -> str:
    """Return encrypted refresh token using ``secret_key``."""
    f = _get_fernet(secret_key)
    return f.encrypt(token.encode()).decode()


def decrypt_refresh_token(token: str, secret_key: str) -> str:
    """Return decrypted refresh token using ``secret_key``."""
    f = _get_fernet(secret_key)
    return f.decrypt(token.encode()).decode()


# ---------------------------------------------------------------------------
# Token refresh
# ---------------------------------------------------------------------------


def refresh_access_token(refresh_token: str, client_id: str) -> dict:
    """Refresh an access token synchronously."""
    data = {
        "client_id": client_id,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    response = requests.post(_GOOGLE_TOKEN_URL, data=data, timeout=10)
    response.raise_for_status()
    return response.json()


async def async_refresh_access_token(refresh_token: str, client_id: str) -> dict:
    """Refresh access token in a thread for async contexts."""

    def _refresh() -> dict:
        return refresh_access_token(refresh_token, client_id)

    return await asyncio.to_thread(_refresh)


__all__ = [
    "build_authorization_url",
    "decrypt_refresh_token",
    "encrypt_refresh_token",
    "exchange_code_for_token",
    "generate_code_challenge",
    "generate_code_verifier",
    "refresh_access_token",
    "async_refresh_access_token",
]
