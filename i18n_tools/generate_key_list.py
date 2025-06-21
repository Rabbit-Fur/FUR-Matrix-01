import json
from pathlib import Path

DEFAULT_SOURCE = Path("translations/en.json")
DEFAULT_TARGET = Path("translation_keys.json")


def update_key_list(source: Path = DEFAULT_SOURCE, target: Path = DEFAULT_TARGET) -> list[str]:
    """Generate sorted translation key list from the given source file."""
    if not source.exists():
        raise FileNotFoundError(f"Missing translation file: {source}")

    with source.open(encoding="utf-8") as f:
        data = json.load(f)

    keys = sorted(data.keys())
    target.write_text(json.dumps(keys, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return keys


if __name__ == "__main__":
    keys = update_key_list()
    print(f"✅ Generated {len(keys)} translation keys.")
