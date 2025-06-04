"""
config.py – Zentrale Projekt-Konfiguration (Flask, Discord, System, i18n, Uploads)

Lädt alle benötigten Einstellungen aus Umgebungsvariablen oder .env-Datei und hält sie typsicher in der Config-Klasse bereit.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv
from utils.env_helpers import get_env_str, get_env_int, get_env_bool
from fur_lang.i18n import get_supported_languages

# 📍 .env Pfad dynamisch bestimmbar via ENV_FILE, sonst Fallback zu ./env
basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.environ.get("ENV_FILE", os.path.join(basedir, ".env"))
load_dotenv(env_path)

class Config:
    """
    Zentrale Config-Klasse für alle Flask- und System-Settings.

    Werte werden nach Best Practice aus der Umgebung geladen.
    """

    # --- Flask Core ---
    SECRET_KEY: str = get_env_str("SECRET_KEY", default="dev-secret-key-CHANGE-ME-IN-PROD")
    FLASK_ENV: str = get_env_str("FLASK_ENV", default="development")
    DEBUG: bool = FLASK_ENV == "development"

    # --- Security ---
    SESSION_COOKIE_SECURE: bool = FLASK_ENV == "production"
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    PERMANENT_SESSION_LIFETIME: timedelta = timedelta(
        minutes=get_env_int("SESSION_LIFETIME_MINUTES", default=60)
    )
    WTF_CSRF_ENABLED: bool = True

    # --- Database ---
    DATABASE_PATH: str = os.path.join(basedir, "data", "admin_users.db")

    # --- Discord Integration ---
    DISCORD_WEBHOOK_URL: str | None = get_env_str("DISCORD_WEBHOOK_URL", required=False)
    DISCORD_TOKEN: str = get_env_str("DISCORD_TOKEN", required=True)
    DISCORD_GUILD_ID: int = get_env_int("DISCORD_GUILD_ID", required=True)
    DISCORD_CHANNEL_ID: int = get_env_int("DISCORD_CHANNEL_ID", required=True)
    DISCORD_CLIENT_ID: str | None = get_env_str("DISCORD_CLIENT_ID", required=False)
    DISCORD_CLIENT_SECRET: str | None = get_env_str("DISCORD_CLIENT_SECRET", required=False)
    DISCORD_REDIRECT_URI: str | None = get_env_str("DISCORD_REDIRECT_URI", required=False)
    
    # BABEL / i18n
    BABEL_DEFAULT_LOCALE = "de"
    BABEL_SUPPORTED_LOCALES = get_supported_languages()

    # --- Internationalization ---
    SUPPORTED_LANGUAGES: list[str] = [
        "en", "de", "vi", "tr", "it", "cs", "es", "fr", "pl", "ru"
    ]
    DEFAULT_LANGUAGE: str = "en"

    # --- Poster & Medal Generation ---
    STATIC_FOLDER: str = os.path.join(basedir, "static")
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
    MOTTOS: list[str] = [
        "Forged in Unity",
        "Strength Through Honor",
        "We Never Give Up",
        "Rise Together",
        "Fire in Our Veins",
        "Glory Awaits",
        "Wolves Among Sheep",
    ]
    IMG_WIDTH: int = 1280
    IMG_HEIGHT: int = 720
    TEXT_COLOR: tuple[int, int, int] = (255, 215, 0)
    ROLE_COLOR: tuple[int, int, int] = (255, 100, 100)
    CHAMPION_TEXT_COLOR: tuple[int, int, int] = (255, 215, 0)
    CHAMPION_USERNAME_COLOR: tuple[int, int, int] = (255, 255, 255)
    CHAMPION_SUBTEXT_COLOR: tuple[int, int, int] = (200, 200, 200)
    CHAMPION_BG_COLOR: str = "#0a0a0a"
    MEDAL_SIZE: tuple[int, int] = (150, 150)
    MEDAL_POSITION: tuple[int, int] = (1000, 50)

    # --- Upload Settings ---
    UPLOAD_FOLDER: str = os.path.join(STATIC_FOLDER, "uploads")
    ALLOWED_EXTENSIONS: set[str] = {"jpg", "png"}
    MAX_CONTENT_LENGTH: int = 2 * 1024 * 1024  # 2 MB

    # --- Bot Specific ---
    BOT_PREFIX: str = "!"
    EVENT_REMINDER_CHANNEL: str = "events"
    CHAMPION_ANNOUNCEMENT_CHANNEL: str = "announcements"

    # --- Base URL ---
    BASE_URL: str = get_env_str("BASE_URL", default="http://localhost:8080")
