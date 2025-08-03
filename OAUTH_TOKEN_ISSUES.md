# OAuth Token Issues Report

## utils/oauth_utils.py
- Lines 70-94: Missing `client_secret` in token exchange and no error logging.
  - Added `client_secret` parameter, status logging and error handling.

## web/routes/google_oauth_web.py
- Lines 18-23: `REDIRECT_URI` used a hardcoded default value.
  - Now strictly requires `GOOGLE_REDIRECT_URI` environment variable.
