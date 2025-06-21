"""
i18n.py – Internationalisierung (i18n) für das FUR-System

Lädt Übersetzungen aus /translations/*.json,
stellt zentrale Hilfsfunktionen für Templates, Cogs und Routen bereit.
"""

import json
import logging
import os

from flask import current_app, session

log = logging.getLogger(__name__)

TRANSLATION_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "translations")
LANG_FALLBACK = "de"


def load_translations(directory=TRANSLATION_FOLDER):
    """Lädt alle JSON-Dateien aus dem Übersetzungsordner."""
    translations = {}
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            lang_code = filename.replace(".json", "")
            try:
                with open(os.path.join(directory, filename), encoding="utf-8") as f:
                    translations[lang_code] = json.load(f)
            except Exception as e:
                log.warning(f"⚠️ Fehler beim Laden von {filename}: {e}")
    return translations


# 📦 Globale Übersetzungstabelle
translations = load_translations()


def get_supported_languages():
    """Gibt alle unterstützten Sprachen zurück (z. B. ['de', 'en', 'tr'])."""
    return list(translations.keys())


def current_lang() -> str:
    """Ermittelt die aktuelle Sprache aus der Session oder Default-Konfiguration."""
    return session.get("lang", current_app.config.get("BABEL_DEFAULT_LOCALE", LANG_FALLBACK))


def t(key: str, default: str = None, lang: str = None, **kwargs) -> str:
    """
    Holt die Übersetzung für den gegebenen Key.
    Unterstützt optionale {variablen} im Text via kwargs.

    Args:
        key (str): Übersetzungsschlüssel
        default (str): Fallback-Text, falls Key fehlt
        lang (str): Sprachcode (z. B. "de", "en") – sonst aus Session
        kwargs: Platzhalterwerte für .format()

    Returns:
        str: Übersetzter und formatierter Text
    """
    active_lang = lang or current_lang()
    raw = translations.get(active_lang, {}).get(key, default or key)
    try:
        return raw.format(**kwargs)
    except Exception:
        return raw  # Fallback falls format(...) fehlschlägt
