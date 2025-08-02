#!/usr/bin/env python3

"""Parse files in the ``Wissen`` directory and prepare Mongo-ready JSON."""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

import pytesseract
from bs4 import BeautifulSoup
from docx import Document
from pdf2image import convert_from_path
from pdfminer.high_level import extract_text as pdf_extract_text
from PIL import Image


class EventSchema(dict):
    required_keys = [
        "name",
        "typ",
        "dauer",
        "wiederholung",
        "belohnungen",
        "empfohlen_fuer",
        "beschreibung",
        "tipps",
        "fur_tipps",
    ]

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        for key in self.required_keys:
            self.setdefault(
                key,
                "" if key not in {"belohnungen", "empfohlen_fuer", "tipps", "fur_tipps"} else [],
            )
        self.validate()

    def validate(self) -> None:
        for key in self.required_keys:
            if key not in self:
                raise ValueError(f"Missing key: {key}")


class ShopSchema(dict):
    required_keys = [
        "name",
        "kategorie",
        "preis_euro",
        "preis_diamanten",
        "inhalt",
        "gesamtwert_diamanten",
        "laufzeit",
        "besonderheiten",
    ]

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        for key in self.required_keys:
            self.setdefault(
                key,
                "" if key not in {"preis_euro", "preis_diamanten", "gesamtwert_diamanten"} else [],
            )
        self.setdefault("inhalt", [])
        self.setdefault("besonderheiten", [])
        self.validate()

    def validate(self) -> None:
        for key in self.required_keys:
            if key not in self:
                raise ValueError(f"Missing key: {key}")


class GeneralSchema(dict):
    required_keys = ["titel", "typ", "beschreibung", "fur_tipps", "relevanz_fuer", "quelle"]

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        for key in self.required_keys:
            self.setdefault(key, "" if key not in {"fur_tipps", "relevanz_fuer"} else [])
        self.validate()

    def validate(self) -> None:
        for key in self.required_keys:
            if key not in self:
                raise ValueError(f"Missing key: {key}")


def extract_text(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        try:
            return pdf_extract_text(str(path))
        except Exception:
            images = convert_from_path(str(path))
            return "\n".join(pytesseract.image_to_string(img) for img in images)
    if ext in {".png", ".jpg", ".jpeg"}:
        return pytesseract.image_to_string(Image.open(path))
    if ext in {".txt", ".md"}:
        return path.read_text(errors="ignore")
    if ext in {".html", ".htm"}:
        soup = BeautifulSoup(path.read_text(errors="ignore"), "html.parser")
        return soup.get_text(" ")
    if ext == ".docx":
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
    return ""


def categorize(text: str) -> str:
    lower = text.lower()
    event_kw = ["event", "bank war", "monster truck", "daily clash"]
    shop_kw = ["angebot", "deal", "coins", "abo", "pass", "shop"]
    if any(k in lower for k in event_kw):
        return "event"
    if any(k in lower for k in shop_kw):
        return "shop"
    return "general"


def dedupe_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def save_raw_text(base_out: Path, rel_path: Path, text: str) -> None:
    target = base_out / rel_path.with_suffix(".txt")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)


def create_json(base_out: Path, category: str, name: str, data: Dict[str, Any]) -> None:
    out_dir = base_out / "mongo" / "ki_all" / category
    out_dir.mkdir(parents=True, exist_ok=True)
    file_path = out_dir / f"{name}.json"
    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse Wissen files for KI modules")
    parser.add_argument("--input", default="Wissen", help="Input directory")
    parser.add_argument("--output", default=".", help="Output base directory")
    args = parser.parse_args()

    in_dir = Path(args.input)
    out_base = Path(args.output)
    raw_base = out_base / "raw_text"

    all_events: List[Dict[str, Any]] = []
    all_shops: List[Dict[str, Any]] = []
    all_general: List[Dict[str, Any]] = []
    seen_hashes: set[str] = set()

    for file in in_dir.rglob("*"):
        if not file.is_file():
            continue
        if file.suffix.lower() not in {
            ".pdf",
            ".png",
            ".jpg",
            ".jpeg",
            ".txt",
            ".docx",
            ".html",
            ".htm",
            ".md",
        }:
            continue
        text = extract_text(file)
        if not text.strip():
            continue
        save_raw_text(raw_base, file.relative_to(in_dir), text)
        h = dedupe_hash(text)
        if h in seen_hashes:
            continue
        seen_hashes.add(h)
        category = categorize(text)
        name = file.stem
        if category == "event":
            data = EventSchema(name=name, beschreibung=text, typ="", dauer="", wiederholung="")
            create_json(out_base, "event", name, data)
            all_events.append(dict(data))
        elif category == "shop":
            data = ShopSchema(
                name=name,
                kategorie="",
                preis_euro=0,
                preis_diamanten=0,
                gesamtwert_diamanten=0,
                laufzeit="",
            )
            create_json(out_base, "shop", name, data)
            all_shops.append(dict(data))
        else:
            data = GeneralSchema(titel=name, typ="Strategie", beschreibung=text, quelle=str(file))
            create_json(out_base, "general", name, data)
            all_general.append(dict(data))

    if all_events:
        (out_base / "events_all.json").write_text(
            json.dumps(all_events, ensure_ascii=False, indent=2)
        )
    if all_shops:
        (out_base / "shop_all.json").write_text(json.dumps(all_shops, ensure_ascii=False, indent=2))
    if all_general:
        (out_base / "general_all.json").write_text(
            json.dumps(all_general, ensure_ascii=False, indent=2)
        )


if __name__ == "__main__":
    main()
