"""
translation_auto.py – Automatisches Extrahieren und Übersetzen von UI-Texten

Dieses Skript sucht in Quellcode und Templates nach allen Aufrufen von ``t(“…”)`` und schreibt sie als JSON-Datei,  # noqa: E501
übersetzt sie bei Bedarf automatisiert via OpenAI GPT (oder kopiert sie als Fallback)  # noqa: E501
und schreibt das Ergebnis als JSON-Translation-File für Flask-Babel/i18n.  # noqa: E501
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import List, Set

import openai

# === Konfiguration ===
SOURCE_DIRS = [".", "templates"]
TARGET_LANG = "de"
TRANSLATION_FILE = Path(f"translations/{TARGET_LANG}.json")
USE_GPT = True  # Für Tests False setzen, dann nur Kopie

log = logging.getLogger(__name__)

# === API Key setzen ===
openai.api_key = os.getenv("OPENAI_API_KEY")
if USE_GPT and not openai.api_key:
    raise EnvironmentError("❌ OPENAI_API_KEY ist nicht gesetzt.")


def scan_translation_keys() -> List[str]:
    """
    Scans all source directories for calls to `t` ('Text') and returns a sorted list of keys.

    Returns:
        List[str]: Alphabetically sorted list of all found keys.
    """
    pattern = re.compile(r"t\(\s*['\"](.+?)['\"]\s*\)")
    found_keys: Set[str] = set()

    for folder in SOURCE_DIRS:
        for path in Path(folder).rglob("*"):
            if path.suffix in {".py", ".html", ".jinja", ".jinja2"} and path.is_file():
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    matches = pattern.findall(content)
                    if matches:
                        found_keys.update(matches)
                except Exception as e:
                    log.error("⚠️ Fehler beim Lesen von %s: %s", path, e)
    return sorted(found_keys)


def translate_gpt(text: str) -> str:
    """
    Übersetzt einen String ins Deutsche via OpenAI GPT.

    Args:
        text (str): Zu übersetzender Text.

    Returns:
        str: Übersetzung (oder Original bei Fehler).
    """
    try:
        log.info("🌍 GPT übersetzt: '%s'", text)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Übersetze folgenden Text für eine Benutzeroberfläche ins Deutsche: '{text}'",  # noqa: E501
                }
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        log.error("❌ GPT-Fehler bei '%s': %s", text, e)
        return text


def update_translation_file(keys: List[str]) -> None:
    """
    Aktualisiert oder erzeugt die JSON-Datei mit allen Keys.

    Args:
        keys (List[str]): Liste aller zu übersetzenden Keys.
    """
    TRANSLATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing = {}

    if TRANSLATION_FILE.exists():
        with TRANSLATION_FILE.open(encoding="utf-8") as f:
            existing = json.load(f)

    new_count = 0
    for key in keys:
        if key not in existing:
            existing[key] = translate_gpt(key) if USE_GPT else key
            new_count += 1

    with TRANSLATION_FILE.open("w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    log.info("✅ %s neue Übersetzungen hinzugefügt.", new_count)
    log.info("📁 Datei gespeichert: %s", TRANSLATION_FILE)


if __name__ == "__main__":
    log.info("🔍 Scanne Quellverzeichnisse nach t('…') Keys ...")
    keys = scan_translation_keys()
    log.info("🔑 %s eindeutige Keys gefunden.", len(keys))
    update_translation_file(keys)