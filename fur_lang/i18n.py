import json
import os

from flask import current_app, session

TRANSLATION_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "translations"
)


def load_translations(directory=TRANSLATION_FOLDER):
    translations = {}
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            lang_code = filename.replace(".json", "")
            with open(os.path.join(directory, filename), encoding="utf-8") as f:
                try:
                    translations[lang_code] = json.load(f)
                except Exception as e:
                    print(f"⚠️ Fehler beim Laden von {filename}: {e}")
    return translations


translations = load_translations()


def get_supported_languages():
    return list(translations.keys())


def t(key: str, default=None):
    lang = session.get("lang", current_app.config.get("BABEL_DEFAULT_LOCALE", "de"))
    return translations.get(lang, {}).get(key, default or key)
