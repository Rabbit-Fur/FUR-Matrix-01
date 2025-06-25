from pathlib import Path
from typing import List


def cleanup_flags(
    flag_dir: str | Path = "static/flags",
    translations_dir: str | Path = "translations",
) -> List[str]:
    """Delete flag PNG files without matching translation JSON.

    Args:
        flag_dir: Directory containing ``*.png`` flag images.
        translations_dir: Directory containing ``*.json`` translations.

    Returns:
        List of removed flag file names.
    """
    flag_path = Path(flag_dir)
    translations_path = Path(translations_dir)
    removed: List[str] = []
    for flag_file in flag_path.glob("*.png"):
        lang_code = flag_file.stem
        if not (translations_path / f"{lang_code}.json").exists():
            flag_file.unlink()
            removed.append(flag_file.name)
    return removed


if __name__ == "__main__":
    removed = cleanup_flags()
    if removed:
        print(f"🧹 Removed {len(removed)} unused flags: {', '.join(removed)}")
    else:
        print("✅ No unused flag icons found.")
