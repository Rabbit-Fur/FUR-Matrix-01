import json
from pathlib import Path
from typing import Dict, Set

import requests

TRANSLATIONS_DIR = Path("translations")
BASE_LANG = "en"
API_URL = "https://translate.argosopentech.com/translate"


def load_all() -> Dict[str, Dict[str, str]]:
    data = {}
    for path in TRANSLATIONS_DIR.glob("*.json"):
        with path.open(encoding="utf-8") as f:
            try:
                data[path.stem] = json.load(f)
            except json.JSONDecodeError:
                data[path.stem] = {}
    return data


def save_lang(lang: str, entries: Dict[str, str]):
    path = TRANSLATIONS_DIR / f"{lang}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def translate(text: str, target: str) -> str:
    if target == BASE_LANG:
        return text
    payload = {"q": text, "source": BASE_LANG, "target": target, "format": "text"}
    try:
        resp = requests.post(API_URL, data=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()["translatedText"]
    except Exception as e:
        print(f"Translation error [{target}]: {e}")
        return text


def main() -> None:
    data = load_all()
    base = data.get(BASE_LANG, {})
    all_keys: Set[str] = set(base.keys())
    for d in data.values():
        all_keys.update(d.keys())

    for lang, entries in data.items():
        missing = [k for k in all_keys if k not in entries]
        if not missing:
            continue
        print(f"{lang}: adding {len(missing)} translations")
        for key in missing:
            source_text = base.get(key, key)
            entries[key] = translate(source_text, lang)
        save_lang(lang, entries)


if __name__ == "__main__":
    main()
