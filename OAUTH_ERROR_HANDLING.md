# OAuth Error Handling Report

This document summarizes updates to error handling for Google OAuth token exchange.

| File/Line | Old Output | New Output |
|-----------|-----------|-----------|
| `google_auth.py` L137 | `{"error": "token_failed", "details": text}` | `{"error": "token_failed", "details": text or str(exc)}` |
| `web/routes/google_oauth_web.py` L94 | `{"error": f"Authentication failed: {exc}", "details": text}` (could be null) | `{"error": f"Authentication failed: {exc}", "details": text or str(exc)}` |

Both locations now log the response status and text and ensure the API response contains the full Google error message. Automated tests check that `details` is never `None`.
