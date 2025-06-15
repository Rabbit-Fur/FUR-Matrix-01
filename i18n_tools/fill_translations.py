import json
from pathlib import Path

import requests

TRANSLATION_DIR = Path("translations")
BASE_LANG = "de"
MISSING_FILE = Path("missing_translations.md")
API_URL = "https://api.mymemory.translated.net/get"


def get_languages():
    return [p.stem for p in TRANSLATION_DIR.glob("*.json") if p.stem != BASE_LANG]


def translate_text(text: str, target: str) -> str | None:
    if target == BASE_LANG:
        return text
    try:
        params = {"q": text, "langpair": f"{BASE_LANG}|{target}"}
        resp = requests.get(API_URL, params=params, timeout=10, verify=False)
        resp.raise_for_status()
        data = resp.json()
        return data.get("responseData", {}).get("translatedText")
    except Exception as e:
        print(f"Translation error for {target}: {e}")
        return None


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_json(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(dict(sorted(data.items())), f, indent=2, ensure_ascii=False)


def main() -> None:
    base = load_json(TRANSLATION_DIR / f"{BASE_LANG}.json")
    languages = get_languages()
    missing_entries = []

    for lang in languages:
        path = TRANSLATION_DIR / f"{lang}.json"
        data = load_json(path)
        updated = False

        for key, value in base.items():
            if key not in data or not data[key]:
                translated = translate_text(value, lang)
                if not translated or translated.strip() == value:
                    data[key] = "TODO"
                    missing_entries.append(f"- [{lang}] {key} → (TODO)")
                else:
                    data[key] = translated
                updated = True

        if updated:
            save_json(path, data)

    if missing_entries:
        lines = [
            "# 🚫 Fehlende/unklare Übersetzungen",
            "",
            "Diese Begriffe konnten nicht automatisch sicher übersetzt werden. Bitte manuell nachtragen:",
            "",
        ]
        lines.extend(missing_entries)
        MISSING_FILE.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
