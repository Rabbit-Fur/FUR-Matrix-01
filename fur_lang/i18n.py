"""
i18n.py – Internationalisierung (i18n) für das FUR-System

Lädt Übersetzungen aus /translations/*.json,
stellt zentrale Hilfsfunktionen für Templates, Cogs und Routen bereit.
"""

import json
import logging
import os
from typing import Any

from babel import Locale
from flask import current_app, request, session

log = logging.getLogger(__name__)

TRANSLATION_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "translations")
FLAG_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "flags")
LANG_FALLBACK = "en"


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


def _save_translation(lang: str, key: str, value: str) -> None:
    """Persist a new translation entry to disk."""
    translations.setdefault(lang, {})[key] = value
    path = os.path.join(TRANSLATION_FOLDER, f"{lang}.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(translations[lang], f, indent=2, ensure_ascii=False)
    except Exception as exc:  # noqa: BLE001
        log.error("Failed saving translation %s:%s – %s", lang, key, exc)


def warn_flags_without_translation(
    flag_dir: str = FLAG_FOLDER, translation_dir: str = TRANSLATION_FOLDER
) -> None:
    """Log a warning for each flag without matching translation file."""
    for flag_file in os.listdir(flag_dir):
        if not flag_file.endswith(".png"):
            continue
        lang_code = flag_file[:-4]
        json_path = os.path.join(translation_dir, f"{lang_code}.json")
        if not os.path.exists(json_path):
            log.warning("Flag '%s' found but no %s.json translation.", flag_file, lang_code)


warn_flags_without_translation()


def get_language_native_name(lang: str) -> str:
    """Return the native name of a language code."""
    try:
        locale = Locale.parse(lang)
        return locale.get_display_name(lang)
    except Exception:  # pragma: no cover - fallback
        return lang


def is_rtl(lang: str) -> bool:
    """Return True if language is right-to-left."""
    try:
        return Locale.parse(lang).text_direction == "rtl"
    except Exception:  # pragma: no cover - fallback
        return False


def get_supported_languages() -> list[str]:
    """Return all available language codes sorted alphabetically."""
    if not translations:
        translations.update(load_translations())
    return sorted(translations.keys())


def current_lang() -> str:
    """Ermittelt die aktuelle Sprache aus Session oder Accept-Language."""
    try:
        lang = session.get("lang")
    except RuntimeError:
        lang = None
    if not lang:
        try:
            lang = request.accept_languages.best_match(get_supported_languages())
        except RuntimeError:
            lang = None
    if not lang:
        lang = current_app.config.get("BABEL_DEFAULT_LOCALE", LANG_FALLBACK)
    return lang


def t(
    key: str,
    default: str | None = None,
    lang: str | None = None,
    count: int | None = None,
    **kwargs: Any,
) -> str:
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
    if active_lang not in translations or not translations.get(active_lang):
        translations.update(load_translations())

    entry = translations.get(active_lang, {}).get(key)
    if isinstance(entry, dict) and count is not None:
        raw = entry.get("one" if count == 1 else "other")
    else:
        raw = entry

    if raw is None and active_lang != LANG_FALLBACK:
        fallback_entry = translations.get(LANG_FALLBACK, {}).get(key)
        if isinstance(fallback_entry, dict) and count is not None:
            raw = fallback_entry.get("one" if count == 1 else "other")
        else:
            raw = fallback_entry

    if raw is None:
        dev = os.getenv("FLASK_ENV") != "production"
        raw = default or (f"MISSING: {key}" if dev else (default or ""))
        log.warning("Missing translation for '%s'", key)
        if "en" not in translations or key not in translations.get("en", {}):
            _save_translation("en", key, default or key)

    try:
        return str(raw).format(**kwargs)
    except Exception:  # pragma: no cover - formatting errors
        return str(raw)
