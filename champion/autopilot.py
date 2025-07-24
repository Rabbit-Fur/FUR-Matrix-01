"""Automated champion announcement via Discord webhook."""

from __future__ import annotations

import logging
from typing import Optional

from champion.webhook import send_discord_webhook
from utils.champion_data import generate_champion_poster
from config import Config


def run_champion_autopilot(month: Optional[str] = None, username: Optional[str] = None) -> bool:
    """Post a champion announcement poster via the Discord webhook.

    Parameters
    ----------
    month:
        Optional month label to announce, e.g. ``"June"``.
    username:
        Name that should appear on the poster.

    Returns
    -------
    bool
        ``True`` if sending succeeded, otherwise ``False``.
    """

    username = username or "Champion"
    try:
        poster_path = generate_champion_poster(username)
        poster_url = (
            poster_path
            if poster_path.startswith("http")
            else Config.BASE_URL.rstrip("/") + "/" + poster_path.lstrip("/")
        )
        if month:
            content = f"\U0001f3c6 Champion for {month} crowned!"
        else:
            content = "\U0001f3c6 New Champion crowned!"
        status = send_discord_webhook(content=content, image_url=poster_url)
        if status // 100 != 2:
            logging.warning(
                "Champion autopilot webhook returned status %s for %s", status, username
            )
            return False

        logging.info("Champion autopilot executed for %s in %s", username, month)
        return True
    except Exception:  # noqa: BLE001
        logging.exception("Champion autopilot failed")
        return False
