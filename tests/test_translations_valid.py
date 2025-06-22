import json
from pathlib import Path

import pytest

TRANSLATIONS_DIR = Path(__file__).resolve().parents[1] / "translations"


@pytest.mark.parametrize("path", sorted(TRANSLATIONS_DIR.glob("*.json")))
def test_translation_file_valid(path):
    with open(path, encoding="utf-8") as f:
        json.load(f)
