from agents.webhook_agent import WebhookAgent
from config import Config
from utils.champion_data import generate_champion_poster


def post_champion_poster(username: str = "Champion") -> bool:
    """Generate a champion poster and post it via ``WebhookAgent``.

    Parameters
    ----------
    username:
        Name that should appear on the poster.

    Returns
    -------
    bool
        ``True`` if posting succeeded, otherwise ``False``.
    """
    poster_path = generate_champion_poster(username)
    poster_url = (
        poster_path
        if poster_path.startswith("http")
        else Config.BASE_URL.rstrip("/") + "/" + poster_path.lstrip("/")
    )
    webhook = WebhookAgent(Config.DISCORD_WEBHOOK_URL)
    content = f"\U0001f3c6 {username} wurde Champion!"
    return webhook.send(content=content, image_url=poster_url)
