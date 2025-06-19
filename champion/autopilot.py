"""Automated champion announcement via Discord webhook."""

from champion.webhook import send_discord_webhook
from utils.champion_data import generate_champion_poster


def run_champion_autopilot():
    poster_path = generate_champion_poster()
    send_discord_webhook(content="🏆 New Champion crowned!", file_path=poster_path)
