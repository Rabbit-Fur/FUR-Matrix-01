import os
from datetime import timedelta

from dotenv import load_dotenv

from fur_lang.i18n import get_supported_languages
from utils.env_helpers import get_env_int, get_env_str

basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.environ.get("ENV_FILE", os.path.join(basedir, ".env"))
load_dotenv(env_path)


class Config:
    """Zentrale Config-Klasse für FUR System."""

    # --- Flask Core ---
    SECRET_KEY: str = get_env_str("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in production")

    FLASK_ENV: str = get_env_str("FLASK_ENV", default="development")
    DEBUG: bool = FLASK_ENV == "development"

    # --- Security / Session ---
    SESSION_COOKIE_SECURE: bool = FLASK_ENV == "production"
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "None" if FLASK_ENV == "production" else "Lax"
    PERMANENT_SESSION_LIFETIME: timedelta = timedelta(
        minutes=get_env_int("SESSION_LIFETIME_MINUTES", default=60)
    )
    WTF_CSRF_ENABLED: bool = True

    # --- Database ---
    MONGODB_URI: str = get_env_str(
        "MONGODB_URI",
        required=False,
        default=os.getenv("MONGODB_URI"),
    )

    # --- Discord Integration ---
    DISCORD_WEBHOOK_URL: str | None = get_env_str("DISCORD_WEBHOOK_URL", required=False)
    DISCORD_TOKEN: str = get_env_str("DISCORD_TOKEN", required=True)
    DISCORD_GUILD_ID: int = get_env_int("DISCORD_GUILD_ID", required=True)
    REMINDER_CHANNEL_ID: int = get_env_int("REMINDER_CHANNEL_ID", required=True)
    EVENT_CHANNEL_ID: int | None = get_env_int("EVENT_CHANNEL_ID", required=False)
    DISCORD_EVENT_CHANNEL_ID: int | None = EVENT_CHANNEL_ID
    REMINDER_ROLE_ID: int | None = get_env_int("REMINDER_ROLE_ID", required=False)
    DISCORD_CLIENT_ID: str = get_env_str("DISCORD_CLIENT_ID", required=True)
    DISCORD_CLIENT_SECRET: str = get_env_str("DISCORD_CLIENT_SECRET", required=True)
    DISCORD_REDIRECT_URI: str = get_env_str("DISCORD_REDIRECT_URI", required=True)

    R3_ROLE_IDS: set[str] = set(filter(None, get_env_str("R3_ROLE_IDS", default="").split(",")))
    R4_ROLE_IDS: set[str] = set(filter(None, get_env_str("R4_ROLE_IDS", default="").split(",")))
    ADMIN_ROLE_IDS: set[str] = set(
        filter(None, get_env_str("ADMIN_ROLE_IDS", default="").split(","))
    )

    # --- Google Calendar ---
    GOOGLE_CALENDAR_ID: str | None = get_env_str("GOOGLE_CALENDAR_ID", required=False)
    GOOGLE_SYNC_INTERVAL_MINUTES: int = get_env_int(
        "GOOGLE_SYNC_INTERVAL_MINUTES", required=False, default=2
    )
    GOOGLE_REDIRECT_URI: str | None = get_env_str("GOOGLE_REDIRECT_URI", required=False)
    GOOGLE_CREDENTIALS_FILE: str | None = get_env_str(
        "GOOGLE_CREDENTIALS_FILE",
        required=False,
        default=os.path.join(basedir, "credentials", "oauth_client.json"),
    )
    GOOGLE_CALENDAR_SCOPES: list[str] = get_env_str(
        "GOOGLE_CALENDAR_SCOPES",
        default="https://www.googleapis.com/auth/calendar.readonly",
    ).split(",")

    # --- i18n ---
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_SUPPORTED_LOCALES = get_supported_languages()
    SUPPORTED_LANGUAGES: list[str] = [
        "en",
        "de",
        "vi",
        "tr",
        "it",
        "cs",
        "es",
        "fr",
        "pl",
        "ru",
    ]
    DEFAULT_LANGUAGE: str = "en"

    # --- Upload & Poster ---
    STATIC_FOLDER: str = os.path.join(basedir, "static")
    UPLOAD_FOLDER: str = os.path.join(STATIC_FOLDER, "uploads")
    RESOURCES_FOLDER: str = os.path.join(STATIC_FOLDER, "resources")
    ALLOWED_EXTENSIONS: set[str] = {"jpg", "png"}
    MAX_CONTENT_LENGTH: int = 2 * 1024 * 1024

    POSTER_OUTPUT_PATH: str = get_env_str(
        "POSTER_OUTPUT_PATH", default=os.path.join(STATIC_FOLDER, "posters")
    )
    POSTER_OUTPUT_REL_PATH: str = "temp"
    MEDAL_OUTPUT_REL_PATH: str = "medals"
    CHAMPION_OUTPUT_REL_PATH: str = "champions"
    POSTER_FONT_TITLE_PATH: str = os.path.join(STATIC_FOLDER, "fonts/FUR-Bold.ttf")
    POSTER_FONT_TEXT_PATH: str = os.path.join(STATIC_FOLDER, "fonts/FUR-Regular.ttf")
    POSTER_BG_DEFAULT_PATH: str = os.path.join(STATIC_FOLDER, "img/fur_bg.jpg")
    POSTER_BG_TEMPLATES: dict[str, str] = {
        "meeting": "img/meeting_bg.jpg",
        "battle": "img/battle_bg.jpg",
        "training": "img/training_bg.jpg",
        "party": "img/party_bg.jpg",
    }
    MOTTOS = [
        "Forged in Unity",
        "Strength Through Honor",
        "We Never Give Up",
        "Rise Together",
        "Fire in Our Veins",
        "Glory Awaits",
        "Wolves Among Sheep",
    ]
    IMG_WIDTH = 1280
    IMG_HEIGHT = 720
    TEXT_COLOR = (255, 215, 0)
    ROLE_COLOR = (255, 100, 100)
    CHAMPION_TEXT_COLOR = (255, 215, 0)
    CHAMPION_USERNAME_COLOR = (255, 255, 255)
    CHAMPION_SUBTEXT_COLOR = (200, 200, 200)
    CHAMPION_BG_COLOR = "#0a0a0a"
    MEDAL_SIZE = (150, 150)
    MEDAL_POSITION = (1000, 50)

    # --- Bot / Channel ---
    BOT_PREFIX: str = "!"
    EVENT_REMINDER_CHANNEL: str = "events"
    CHAMPION_ANNOUNCEMENT_CHANNEL: str = "announcements"

    # --- Web ---
    BASE_URL: str = get_env_str("BASE_URL", default="http://localhost:8080")


def is_production() -> bool:
    """Return True if the app runs in production mode."""
    return Config.FLASK_ENV == "production"
