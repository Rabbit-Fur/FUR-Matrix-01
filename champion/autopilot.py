from utils.champion_data import generate_champion_poster
from utils.discord_util import send_discord_webhook


def run_champion_autopilot():
    poster_path = generate_champion_poster()
    send_discord_webhook(content="🏆 New Champion crowned!", file_path=poster_path)
