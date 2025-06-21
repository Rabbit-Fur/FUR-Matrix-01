"""
TranslationAgent – automatisiert Übersetzungen und JSON-Synchronisation
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from i18n_tools.generate_key_list import update_key_list


class TranslationAgent:
    def __init__(self, lang_dir: str | Path = "translations"):
        self.lang_dir = Path(lang_dir)

    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        data: Dict[str, Dict[str, str]] = {}
        for path in self.lang_dir.glob("*.json"):
            try:
                with path.open(encoding="utf-8") as f:
                    data[path.stem] = json.load(f)
            except json.JSONDecodeError:
                data[path.stem] = {}
        return data

    def sync(self) -> None:
        """Synchronise all translation files with a unified key set."""

        data = self._load_translations()

        keys_file = Path("translation_keys.json")
        try:
            keys = update_key_list(self.lang_dir / "en.json", keys_file)
        except Exception as e:  # pragma: no cover - log only
            print(f"⚠️ Failed to update key list: {e}")
            keys = []

        all_keys = set(keys)
        if data:
            all_keys.update(*data.values())

        for lang, entries in data.items():
            missing = [k for k in all_keys if k not in entries]
            if not missing:
                continue
            for key in missing:
                entries[key] = ""
            with (self.lang_dir / f"{lang}.json").open("w", encoding="utf-8") as f:
                json.dump(entries, f, indent=2, ensure_ascii=False)

    def auto_translate_missing(self) -> None:
        """Fill missing translations using the auto_fill helper."""

        from i18n_tools import auto_fill

        self.sync()
        original_dir = auto_fill.TRANSLATIONS_DIR
        auto_fill.TRANSLATIONS_DIR = self.lang_dir
        try:
            data = auto_fill.load_all()
            base = data.get(auto_fill.BASE_LANG, {})
            all_keys = set().union(*data.values()) if data else set()

            for lang, entries in data.items():
                missing = [k for k in all_keys if not entries.get(k)]
                if not missing:
                    continue
                for key in missing:
                    source = base.get(key, key)
                    entries[key] = auto_fill.translate(source, lang)
                auto_fill.save_lang(lang, entries)
        finally:
            auto_fill.TRANSLATIONS_DIR = original_dir
